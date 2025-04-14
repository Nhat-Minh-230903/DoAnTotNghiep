import React from 'react'
import { Formik, Form, Field, ErrorMessage } from 'formik'
import * as Yup from 'yup'
import { useAuth } from '../contexts/AuthContext'
import { toast } from 'react-toastify'

const ChangePasswordSchema = Yup.object().shape({
  currentPassword: Yup.string()
    .required('Vui lòng nhập mật khẩu hiện tại'),
  newPassword: Yup.string()
    .min(6, 'Mật khẩu phải có ít nhất 6 ký tự')
    .required('Vui lòng nhập mật khẩu mới'),
  confirmPassword: Yup.string()
    .oneOf([Yup.ref('newPassword'), null], 'Mật khẩu xác nhận không khớp')
    .required('Vui lòng xác nhận mật khẩu mới')
})

const ChangePassword = () => {
  const { changePassword } = useAuth()

  const handleSubmit = async (values, { setSubmitting, resetForm }) => {
    try {
      await changePassword(values.currentPassword, values.newPassword)
      toast.success('Đổi mật khẩu thành công')
      resetForm()
    } catch (error) {
      toast.error(error.message || 'Đổi mật khẩu thất bại')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="max-w-md mx-auto">
      <h1 className="text-2xl font-bold mb-6">Đổi mật khẩu</h1>
      
      <div className="card">
        <Formik
          initialValues={{
            currentPassword: '',
            newPassword: '',
            confirmPassword: ''
          }}
          validationSchema={ChangePasswordSchema}
          onSubmit={handleSubmit}
        >
          {({ isSubmitting }) => (
            <Form>
              <div className="form-group">
                <label htmlFor="currentPassword">Mật khẩu hiện tại</label>
                <Field
                  type="password"
                  id="currentPassword"
                  name="currentPassword"
                  className="form-control"
                />
                <ErrorMessage name="currentPassword" component="div" className="text-error-color text-sm mt-1" />
              </div>
              
              <div className="form-group">
                <label htmlFor="newPassword">Mật khẩu mới</label>
                <Field
                  type="password"
                  id="newPassword"
                  name="newPassword"
                  className="form-control"
                />
                <ErrorMessage name="newPassword" component="div" className="text-error-color text-sm mt-1" />
              </div>
              
              <div className="form-group">
                <label htmlFor="confirmPassword">Xác nhận mật khẩu mới</label>
                <Field
                  type="password"
                  id="confirmPassword"
                  name="confirmPassword"
                  className="form-control"
                />
                <ErrorMessage name="confirmPassword" component="div" className="text-error-color text-sm mt-1" />
              </div>
              
              <div className="flex justify-end">
                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? 'Đang xử lý...' : 'Đổi mật khẩu'}
                </button>
              </div>
            </Form>
          )}
        </Formik>
      </div>
    </div>
  )
}

export default ChangePassword
