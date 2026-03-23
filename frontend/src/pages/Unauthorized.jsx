import { Link } from "react-router-dom";

const Unauthorized = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded shadow text-center max-w-md">
        <h2 className="text-3xl font-bold text-red-600 mb-4">403 - Unauthorized</h2>
        <p className="text-gray-700 mb-6">
          You do not have permission to access this page.
        </p>
        <Link
          to="/"
          className="inline-block px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Go Back to Home
        </Link>
      </div>
    </div>
  );
};

export default Unauthorized;
