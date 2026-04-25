import request from './request'

export const uploadCSV = (formData: FormData) => {
  return request.post('/import/upload-csv', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const uploadExcel = (formData: FormData) => {
  return request.post('/import/upload-excel', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const previewCSV = (formData: FormData) => {
  return request.post('/import/preview-csv', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const previewExcel = (formData: FormData) => {
  return request.post('/import/preview-excel', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}