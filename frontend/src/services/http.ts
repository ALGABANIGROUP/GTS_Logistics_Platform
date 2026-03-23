// frontend/src/services/http.ts
import type { AxiosInstance } from "axios";
import axiosClient from "../api/axiosClient";

const http: AxiosInstance = axiosClient;

export default http;
export { http };
