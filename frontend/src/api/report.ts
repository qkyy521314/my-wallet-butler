import request from './request'

// ============ 报表查询 ============

export const getSummaryReport = (params: { start_date: string, end_date: string, user_id: number }) => {
  return request.get('/report/summary', { params })
}

export const getCategoryAnalysis = (params: { start_date: string, end_date: string, user_id: number, transaction_type?: string }) => {
  return request.get('/report/category-analysis', { params })
}

export const getTrendAnalysis = (params: { start_date: string, end_date: string, user_id: number, group_by?: string }) => {
  return request.get('/report/trend-analysis', { params })
}

export const getMonthlyReport = (params: { year: number, month: number, user_id: number }) => {
  return request.get('/report/monthly-report', { params })
}

export const getBudgetPerformance = (params: { start_date: string, end_date: string, user_id: number }) => {
  return request.get('/report/budget-performance', { params })
}

// ============ 数据导出 ============

export const exportTransactionsCSV = (params: {
  start_date?: string,
  end_date?: string,
  user_id: number,
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
  user_id: number,
  transaction_type?: string
}) => {
  return request.get('/report/export/excel', {
    params,
    responseType: 'blob'
  })
}

// ============ 数据备份 ============

export const createBackup = (params: { user_id: number }) => {
  return request.post('/report/backup', null, { params })
}

export const listBackups = (params: { user_id: number }) => {
  return request.get('/report/backup/list', { params })
}

export const downloadBackup = (filename: string, params: { user_id: number }) => {
  return request.get(`/report/backup/download/${filename}`, {
    params,
    responseType: 'blob'
  })
}

export const deleteBackup = (filename: string, params: { user_id: number }) => {
  return request.delete(`/report/backup/delete/${filename}`, { params })
}

// ============ 数据恢复 ============

export const restoreFromBackup = (filename: string, params: { user_id: number, mode?: string }) => {
  return request.post('/report/restore', null, { params: { ...params, backup_file: filename } })
}

export const restoreFromUpload = (file: File, params: { user_id: number, mode?: string }) => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/report/restore/upload', formData, {
    params,
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}
