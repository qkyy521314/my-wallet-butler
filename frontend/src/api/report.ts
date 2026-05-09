import request from './request'

// ============ 报表查询 ============

export const getSummaryReport = (params: { start_date: string, end_date: string }) => {
  return request.get('/report/summary', { params })
}

export const getCategoryAnalysis = (params: { start_date: string, end_date: string, transaction_type?: string }) => {
  return request.get('/report/category-analysis', { params })
}

export const getTrendAnalysis = (params: { start_date: string, end_date: string, group_by?: string }) => {
  return request.get('/report/trend-analysis', { params })
}

export const getMonthlyReport = (params: { year: number, month: number }) => {
  return request.get('/report/monthly-report', { params })
}

export const getBudgetPerformance = (params: { start_date: string, end_date: string }) => {
  return request.get('/report/budget-performance', { params })
}

// ============ 数据导出 ============

export const exportTransactionsCSV = (params: {
  start_date?: string,
  end_date?: string,
  transaction_type?: string
}) => {
  return request.get('/report/export/csv', {
    params,
    responseType: 'blob'
  })
}

export const exportTransactionsExcel = (params: {
  start_date?: string,
  end_date?: string,
  transaction_type?: string
}) => {
  return request.get('/report/export/excel', {
    params,
    responseType: 'blob'
  })
}

// ============ 数据备份 ============

export const createBackup = () => {
  return request.post('/report/backup', null)
}

export const listBackups = () => {
  return request.get('/report/backup/list')
}

export const downloadBackup = (filename: string) => {
  return request.get(`/report/backup/download/${filename}`, {
    responseType: 'blob'
  })
}

export const deleteBackup = (filename: string) => {
  return request.delete(`/report/backup/delete/${filename}`)
}

// ============ 数据恢复 ============

export const restoreFromBackup = (filename: string, params: { mode?: string }) => {
  return request.post('/report/restore', null, { params: { ...params, backup_file: filename } })
}

export const restoreFromUpload = (file: File, params: { mode?: string }) => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/report/restore/upload', formData, {
    params,
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
