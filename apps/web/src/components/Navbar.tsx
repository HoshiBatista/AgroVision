import { Link, NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../store/auth";

const links = [
  { to: "/app", label: "Обзор", icon: "⌂", end: true },
  { to: "/app/upload", label: "Анализ", icon: "＋" },
  { to: "/app/examples", label: "Примеры", icon: "▦" },
  { to: "/app/reports", label: "Отчёты", icon: "↗" },
];

export function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  return (
    <header className="sticky top-0 z-30 border-b border-slate-800 bg-slate-950/95 text-white shadow-xl backdrop-blur-xl">
      <div className="mx-auto flex max-w-[1440px] flex-wrap items-center gap-4 px-4 py-3 sm:px-6 lg:flex-nowrap lg:px-8">
        <Link to="/app" className="mr-auto flex shrink-0 items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-2xl bg-lime-300 text-xl">🐑</span>
          <span>
            <span className="block text-base font-black leading-none">АгроВижн</span>
            <span className="mt-1 hidden text-[10px] font-bold uppercase tracking-[0.16em] text-emerald-300 sm:block">Умная ферма</span>
          </span>
        </Link>
        <nav className="order-3 flex w-full gap-1 overflow-x-auto border-t border-white/5 pt-3 lg:order-none lg:w-auto lg:border-0 lg:pt-0">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              end={link.end}
              className={({ isActive }) =>
                `flex shrink-0 items-center gap-2 rounded-xl px-3 py-2 text-sm font-bold transition ${isActive ? "bg-white text-slate-950" : "text-slate-400 hover:bg-white/10 hover:text-white"}`
              }
            >
              <span>{link.icon}</span>{link.label}
            </NavLink>
          ))}
        </nav>
        <div className="ml-auto flex shrink-0 items-center gap-3">
          <div className="hidden text-right xl:block">
            <p className="text-xs font-semibold">{user?.email}</p>
            <p className="text-[10px] text-slate-500">Оператор фермы</p>
          </div>
          <button
            className="rounded-xl border border-white/10 px-3 py-2 text-xs font-bold text-slate-300 transition hover:bg-white/10 hover:text-white"
            onClick={() => { logout(); navigate("/login"); }}
          >
            Выйти
          </button>
        </div>
      </div>
    </header>
  );
}
