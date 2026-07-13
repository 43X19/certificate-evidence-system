from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
base=Path(r'D:\新建文件夹\桌面\暑期实训\docs')
out=base/'选题任务书_提取文本.txt'
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
parts=[]
for p in base.glob('*.docx'):
    parts.append(f'==== {p.name} ====')
    with ZipFile(p) as z:
        xml=z.read('word/document.xml')
    root=ET.fromstring(xml)
    for para in root.findall('.//w:p', ns):
        texts=[t.text or '' for t in para.findall('.//w:t', ns)]
        s=''.join(texts).strip()
        if s:
            parts.append(s)
out.write_text('\n'.join(parts), encoding='utf-8')
print(out)
print('lines', len(parts))
