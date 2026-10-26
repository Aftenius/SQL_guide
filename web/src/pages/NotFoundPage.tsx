import { Link } from "react-router";

import { buttonQuietClass } from "../components/ui";
import { usePageTitle } from "../title";

export function NotFoundPage() {
  usePageTitle("Страница не найдена");

  return (
    <section>
      <h1 className="font-serif text-4xl">Такой страницы нет</h1>
      <p className="mt-3 text-muted">Адрес не совпадает ни с одним шагом курса.</p>
      <Link to="/learn" className={`${buttonQuietClass} mt-6`}>
        Ко всем разделам
      </Link>
    </section>
  );
}
