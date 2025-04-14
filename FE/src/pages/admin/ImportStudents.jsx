import React, { useState } from "react";
import { toast } from "react-toastify";
import { API_URL } from "../../config/constants";
import axios from "axios";

const ImportStudents = () => {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      toast.error("Vui lòng chọn file để tải lên");
      return;
    }

    // Kiểm tra định dạng file
    if (!file.name.endsWith('.csv') && !file.name.endsWith('.xlsx')) {
      toast.error("Chỉ hỗ trợ file CSV hoặc Excel");
      return;
    }

    setLoading(true);
    
    try {
      // Trong môi trường thực tế, bạn sẽ gửi file lên server
      // Đây là mô phỏng cho mục đích demo
      const formData = new FormData();
      formData.append('file', file);
      
      // Mô phỏng API call
      // const response = await axios.post(`${API_URL}/admin/import-students`, formData);
      
      // Mô phỏng kết quả thành công
      setTimeout(() => {
        setResults({
          total: 50,
          success: 48,
          failed: 2,
          errors: [
            { row: 5, error: "Email đã tồn tại trong hệ thống" },
            { row: 23, error: "Thiếu thông tin bắt buộc" }
          ]
        });
        toast.success("Đã nhập dữ liệu sinh viên thành công");
        setLoading(false);
      }, 2000);
      
    } catch (error) {
      console.error("Import error:", error);
      toast.error("Có lỗi xảy ra khi nhập dữ liệu");
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Nhập danh sách sinh viên</h1>
      
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Tải lên file</h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 mb-2">Chọn file CSV hoặc Excel</label>
            <input
              type="file"
              accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
              onChange={handleFileChange}
              className="block w-full text-gray-700 border border-gray-300 rounded py-2 px-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-sm text-gray-500 mt-1">
              File phải có các cột: Họ tên, Email, Mã sinh viên, Lớp
            </p>
          </div>
          
          <div className="flex items-center">
            <button
              type="submit"
              disabled={loading}
              className="bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {loading ? "Đang xử lý..." : "Tải lên và xử lý"}
            </button>
            
            <a 
              href="#" 
              className="ml-4 text-blue-600 hover:text-blue-800"
              onClick={(e) => {
                e.preventDefault();
                toast.info("Đã tải xuống file mẫu");
              }}
            >
              Tải xuống file mẫu
            </a>
          </div>
        </form>
      </div>
      
      {results && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-semibold mb-4">Kết quả nhập liệu</h2>
          
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-gray-100 p-4 rounded-lg text-center">
              <p className="text-gray-600">Tổng số bản ghi</p>
              <p className="text-2xl font-bold">{results.total}</p>
            </div>
            <div className="bg-green-100 p-4 rounded-lg text-center">
              <p className="text-green-600">Thành công</p>
              <p className="text-2xl font-bold text-green-600">{results.success}</p>
            </div>
            <div className="bg-red-100 p-4 rounded-lg text-center">
              <p className="text-red-600">Thất bại</p>
              <p className="text-2xl font-bold text-red-600">{results.failed}</p>
            </div>
          </div>
          
          {results.errors.length > 0 && (
            <div>
              <h3 className="font-semibold mb-2">Lỗi chi tiết:</h3>
              <div className="bg-gray-50 rounded border">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Dòng
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Lỗi
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {results.errors.map((error, index) => (
                      <tr key={index}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {error.row}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-red-500">
                          {error.error}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ImportStudents;
