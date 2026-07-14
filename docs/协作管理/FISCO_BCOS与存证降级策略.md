# FISCO BCOS 与存证降级策略

本文档用于说明联盟链接入的优先级和降级方案。当前项目主线是证书生命周期闭环，FISCO BCOS 是增强能力，不应阻塞发证、验真和撤销演示。

## 1. 优先级定义

| 优先级 | 内容 | 是否阻塞主流程 |
| --- | --- | --- |
| P0 | SHA-256、本地哈希链、回执、扫码验真、撤销 | 是 |
| P1 | 存证记录展示、审计日志、篡改 PDF 验真 | 是 |
| P2 | FISCO BCOS 节点环境、合约部署、链上交易回执 | 否 |
| P3 | Merkle Root、DID/VC、可信简历选择性披露 | 否 |

## 2. 统一存证接口

业务后端不直接依赖具体链实现，只调用统一存证服务。

```text
EvidenceService
├─ saveEvidence(certificateNo, certificateHash, metadata)
├─ getEvidence(receiptId)
└─ verifyEvidence(certificateNo, certificateHash)
```

底层实现可以切换：

```text
EvidenceService
├─ LocalHashChainEvidenceService     # 默认实现，必须完成
└─ FiscoBcosEvidenceService          # 加分实现，时间允许再接入
```

## 3. 本地哈希链方案

### 3.1 保存内容

每条存证记录保存：

| 字段 | 含义 |
| --- | --- |
| `receipt_id` | 回执编号 |
| `certificate_no` | 证书编号 |
| `certificate_hash` | 证书 PDF 的 SHA-256 |
| `previous_hash` | 上一条本地链记录哈希 |
| `current_block_hash` | 当前记录哈希 |
| `block_height` | 本地链高度 |
| `evidence_time` | 存证时间 |
| `status` | 回执状态 |

### 3.2 当前记录哈希口径

建议使用以下字段拼接后计算 SHA-256：

```text
block_height + certificate_no + certificate_hash + previous_hash + evidence_time
```

### 3.3 演示价值

本地哈希链可以展示：

1. 每张证书都有唯一哈希。
2. 每次存证都有回执。
3. 后一条记录依赖前一条记录哈希。
4. 修改 PDF 后哈希不一致，验真失败。

## 4. FISCO BCOS 接入策略

### 4.1 只有满足以下条件才接入

- 本地哈希链已跑通。
- 发证、验真、撤销主流程已跑通。
- 后端存证接口已经稳定。
- 有至少 1 天完整联调时间。

### 4.2 FISCO 最小接入范围

只做最小合约能力：

```text
saveEvidence(certificateNo, certificateHash)
getEvidence(certificateNo)
```

不做复杂权限、多机构治理、跨链、DID/VC 或隐私证明。

### 4.3 链上回执映射

| 本地字段 | FISCO 字段 |
| --- | --- |
| `receipt_id` | 系统生成回执编号 |
| `tx_hash` | 交易哈希 |
| `contract_address` | 合约地址 |
| `block_height` | 区块高度 |
| `evidence_time` | 交易确认时间或系统记录时间 |

## 5. 降级触发条件

遇到以下情况立即降级到本地哈希链：

1. FISCO 节点启动失败超过半天。
2. 合约部署失败且无法快速定位。
3. FISCO SDK、Web3.py、命令行工具或依赖版本冲突影响 FastAPI 后端启动。
4. 链上交易不稳定，导致验真流程无法演示。
5. 前后端主流程尚未跑通。

## 6. 降级后的答辩话术

> 本项目当前实现的是教学版可信存证系统，核心机制是对证书 PDF 计算 SHA-256，并将哈希、时间戳、证书编号和前序哈希写入本地哈希链，形成可追踪回执。这样可以证明证书文件在存证后是否被篡改。系统的存证服务已抽象出统一接口，后续可以将本地哈希链实现替换为 FISCO BCOS 联盟链实现，返回链上交易哈希和区块高度。

## 7. 风险边界

1. 不承诺“绝对防伪”，只证明存证版本未被篡改。
2. 证书当前有效性必须结合 `certificates.status` 和撤销记录判断。
3. 旧回执只能证明曾经存证，不能证明证书现在仍有效。
4. FISCO 是增强项，不应影响 P0 演示闭环。

## 8. Merkle Root 扩展方案（P2，在本地哈希链之上叠加）

本节详细说明第 1 节优先级表里 P2/P3 的“Merkle Root”具体怎么做，前提是第 3 节的本地哈希链方案已经跑通、每张证书都已有独立的哈希和回执。Merkle Root 不替代本地哈希链，是在其之上叠加的可选能力。

### 8.1 解决的问题

本地哈希链保证了“每张证书都能单独验真”，但如果要接测试链，逐张证书都写一笔上链交易成本较高。Merkle Root 把一个批次的所有证书哈希汇总成一个根哈希，一个批次只需要写一笔上链交易，单张证书仍可通过 Merkle Proof 单独验证，不需要暴露批次内其他证书的数据。

### 8.2 结构与触发时机

1. 批次内每张证书的 `certificate_hash` 作为叶子节点，叶子顺序固定按 `certificate_no` 升序排列，避免不同实现算出不同 Root。
2. 相邻叶子两两配对拼接后计算 SHA-256 作为父节点，逐层向上，最终得到一个 Merkle Root。
3. 如果某一层节点数为奇数，固定复制该层最后一个节点作为右节点参与父节点计算，即 `DUPLICATE_LAST` 规则。
4. 父节点拼接口径固定为 `SHA256(left_node_hash + right_node_hash)`，节点哈希使用 64 位小写十六进制字符串。
5. 建树和算 Root 只在批次内所有证书都完成生成和哈希计算之后触发一次，不与单证书生成过程耦合。
6. 详细字段设计和建表 SQL 见 `docs/协作管理/数据库设计.md` 第 9 节。

### 8.3 与撤销的关系

Root 一旦生成即为历史事实，不因撤销重新计算；证书当前是否有效由 `certificates.status` 单独判断，与 Merkle Root/Proof 的验证结果分开展示，具体约束见数据库设计文档第 9.4 节。

### 8.4 与真实测试链的关系

如果按第 4 节的条件接入了 FISCO BCOS 或 Hardhat/Ganache，上链的内容应该只是 Merkle Root（一个批次一笔交易），而不是每张证书单独上链一次，理由同 8.1。降级触发条件不变：真链接入失败时，Root 依然可以只保存在本地 Root 链里（`credential_roots` 表的 `previous_root_hash`/`current_root_hash` 链式结构），不影响验真闭环演示。

