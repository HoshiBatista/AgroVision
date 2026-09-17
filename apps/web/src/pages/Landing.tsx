import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { CloudScene } from "../components/CloudScene";
import { SheepFlock } from "../components/SheepFlock";

const features = [
  {
    icon: "🛰️",
    title: "Живые потоки дронов",
    text: "Несколько видеопотоков одновременно с подсчётом овец в реальном времени.",
  },
  {
    icon: "🖼️",
    title: "Фото и видео",
    text: "Загрузите кадр или ролик — модель разметит и посчитает всё стадо.",
  },
  {
    icon: "📊",
    title: "Дашборд и отчёты",
    text: "Тренды поголовья, задержка модели и экспорт журнала в CSV/PDF.",
  },
];

export function Landing() {
  return (
    <div className="relative min-h-full overflow-hidden">
      <CloudScene />
      <div className="relative z-10">
        <header className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6">
          <span className="flex items-center gap-2 text-xl font-extrabold text-sky-900">
            <span className="text-3xl">🐑</span> АгроВижн
          </span>
          <div className="flex gap-3">
            <Link to="/login" className="btn-ghost">
              Войти
            </Link>
            <Link to="/register" className="btn-primary">
              Регистрация
            </Link>
          </div>
        </header>

        <section className="mx-auto max-w-4xl px-6 pt-16 text-center">
          <motion.h1
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7 }}
            className="text-4xl font-extrabold tracking-tight text-sky-950 sm:text-6xl"
          >
            Считаем овец с высоты птичьего полёта
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.15 }}
            className="mx-auto mt-6 max-w-2xl text-lg text-sky-800"
          >
            АгроВижн анализирует аэрофото и видео с дронов на базе YOLO26 и превращает
            детекции в понятные решения для фермы: сколько овец, где и когда.
          </motion.p>
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.3 }}
            className="mt-10 flex justify-center gap-4"
          >
            <Link to="/register" className="btn-primary px-8 py-3 text-lg">
              Начать бесплатно
            </Link>
            <Link to="/login" className="btn-ghost px-8 py-3 text-lg">
              У меня есть аккаунт
            </Link>
          </motion.div>
        </section>

        <SheepFlock />

        <section className="mx-auto mt-16 grid max-w-6xl gap-6 px-6 pb-24 sm:grid-cols-3">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              className="glass p-6 text-left"
            >
              <div className="text-3xl">{feature.icon}</div>
              <h3 className="mt-3 text-lg font-bold text-slate-800">{feature.title}</h3>
              <p className="mt-2 text-sm text-slate-600">{feature.text}</p>
            </motion.div>
          ))}
        </section>
      </div>
    </div>
  );
}
