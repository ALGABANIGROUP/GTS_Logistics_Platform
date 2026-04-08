// frontend/src/layouts/MainLayout.jsx
import React from "react";
import Navbar from "../components/ui/Navbar.jsx";
import TopUserBar from "../components/TopUserBar.jsx";
import Footer from "../components/ui/Footer.jsx";
import { Outlet } from "react-router-dom";

const MainLayout = () => {
  return (
    <div className="min-h-screen flex bg-slate-50 text-slate-900 dark:bg-slate-800 dark:text-slate-100">
      <Navbar />

      <div className="flex-1 flex flex-col min-w-0">
        <TopUserBar />

        <main className="flex-1 p-6 overflow-y-auto bg-slate-50 dark:bg-slate-800">
          <Outlet />
        </main>

        <Footer />
      </div>
    </div>
  );
};

export default MainLayout;
