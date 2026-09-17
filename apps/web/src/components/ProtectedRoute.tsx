import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../store/auth";
import { Navbar } from "./Navbar";

export function ProtectedRoute() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center text-slate-500">Загрузка…</div>
    );
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return (
    <div className="min-h-full">
      <Navbar />
      <main className="mx-auto max-w-[1440px] px-4 py-7 sm:px-6 lg:px-8">
        <Outlet />
      </main>
    </div>
  );
}
