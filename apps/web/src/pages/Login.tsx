import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { CloudScene } from "../components/CloudScene";
import { useAuth } from "../store/auth";

export function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await login(email, password);
      navigate("/app");
    } catch {
      setError("Неверная электронная почта или пароль");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="relative flex min-h-full items-center justify-center overflow-hidden p-6">
      <CloudScene />
      <form onSubmit={onSubmit} className="glass relative z-10 w-full max-w-md p-8">
        <Link to="/" className="mb-6 flex items-center gap-2 text-xl font-extrabold text-sky-900">
          <span className="text-2xl">🐑</span> АгроВижн
        </Link>
        <h1 className="text-2xl font-bold text-slate-800">С возвращением</h1>
        <p className="mt-1 text-sm text-slate-500">Войдите, чтобы открыть дашборд.</p>

        <div className="mt-6 space-y-4">
          <div>
            <label className="label">Электронная почта</label>
            <input
              type="email"
              required
              className="field"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="operator@farm.com"
            />
          </div>
          <div>
            <label className="label">Пароль</label>
            <input
              type="password"
              required
              className="field"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
            />
          </div>
        </div>

        {error && <p className="mt-4 text-sm font-medium text-red-500">{error}</p>}

        <button type="submit" disabled={busy} className="btn-primary mt-6 w-full py-3">
          {busy ? "Входим…" : "Войти"}
        </button>
        <p className="mt-4 text-center text-sm text-slate-500">
          Нет аккаунта?{" "}
          <Link to="/register" className="font-semibold text-meadow-700">
            Зарегистрироваться
          </Link>
        </p>
      </form>
    </div>
  );
}
