import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { AxiosError } from "axios";
import { CloudScene } from "../components/CloudScene";
import { useAuth } from "../store/auth";

export function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    if (password.length < 8) {
      setError("Пароль должен быть не короче 8 символов");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      await register(email, password);
      navigate("/app");
    } catch (err) {
      const status = (err as AxiosError).response?.status;
      setError(status === 409 ? "Пользователь с такой почтой уже существует" : "Не удалось зарегистрироваться");
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
        <h1 className="text-2xl font-bold text-slate-800">Создать аккаунт</h1>
        <p className="mt-1 text-sm text-slate-500">Бесплатно. Никаких облачных сервисов.</p>

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
              placeholder="минимум 8 символов"
            />
          </div>
        </div>

        {error && <p className="mt-4 text-sm font-medium text-red-500">{error}</p>}

        <button type="submit" disabled={busy} className="btn-primary mt-6 w-full py-3">
          {busy ? "Создаём…" : "Зарегистрироваться"}
        </button>
        <p className="mt-4 text-center text-sm text-slate-500">
          Уже есть аккаунт?{" "}
          <Link to="/login" className="font-semibold text-meadow-700">
            Войти
          </Link>
        </p>
      </form>
    </div>
  );
}
