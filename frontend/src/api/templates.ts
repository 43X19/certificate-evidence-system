import request from '@/utils/request'
import type { PageQuery, PageResult, Template } from '@/types'
import { pageOf, templates, useMock, wait } from './mock'
import { snakeize } from './helpers'

export async function getTemplates(query: PageQuery): Promise<PageResult<Template>> {
  if (useMock) { await wait(); return pageOf(templates, query) }
  const result = await request.get('/admin/templates', { params: snakeize(query) }) as PageResult<Record<string, unknown>>
  return { ...result, records: result.records.map(fromContract) }
}

function fromContract(data: Record<string, unknown>): Template {
  const config = (data.content_config || {}) as Record<string, unknown>
  return {
    template_id: Number(data.template_id),
    name: String(data.template_name || ''),
    issuer: String(data.institution_name || ''),
    course_name: String(config.course_name || ''),
    project_name: String(config.project_name || ''),
    certificate_title: String(config.certificate_title || ''),
    content: String(config.content || ''),
    issue_year: String(config.issue_year || ''),
    fields: Array.isArray(config.fields) ? config.fields.map(String) : [],
    enabled: data.status !== 'DISABLED',
    updated_at: String(data.updated_at || '')
  }
}

function toContract(data: Partial<Template>) {
  return {
    templateName: data.name,
    institutionName: data.issuer,
    contentConfig: {
      course_name: data.course_name,
      project_name: data.project_name,
      certificate_title: data.certificate_title,
      content: data.content,
      issue_year: data.issue_year,
      fields: data.fields
    },
    status: data.enabled ? 'ACTIVE' : 'DISABLED'
  }
}

export async function createTemplate(data: Omit<Template, 'template_id' | 'updated_at'>) {
  if (useMock) { await wait(); templates.unshift({ ...data, template_id: Date.now(), updated_at: new Date().toLocaleString() }); return }
  await request.post('/admin/templates', snakeize(toContract(data)))
}
export async function updateTemplate(id: number, data: Partial<Template>) {
  if (useMock) { await wait(); Object.assign(templates.find(x => x.template_id === id) || {}, data, { updated_at: new Date().toLocaleString() }); return }
  await request.put(`/admin/templates/${id}`, snakeize(toContract(data)))
}
export async function deleteTemplate(id: number) {
  if (useMock) { await wait(); templates.splice(templates.findIndex(x => x.template_id === id), 1); return }
  await request.delete(`/admin/templates/${id}`)
}