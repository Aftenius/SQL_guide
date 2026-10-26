import { createBrowserRouter } from "react-router";

import { lessonCrumb, trackCrumb } from "./catalog";
import { RootLayout } from "./components/RootLayout";
import { LoginPage, RegisterPage } from "./pages/AuthForm";
import { LessonPage, TrackPage, TracksPage } from "./pages/CoursePages";
import { HomePage } from "./pages/HomePage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { YandexCallbackPage } from "./pages/YandexCallbackPage";

export const router = createBrowserRouter([
  {
    element: <RootLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: "login", element: <LoginPage />, handle: { crumb: "Вход" } },
      { path: "register", element: <RegisterPage />, handle: { crumb: "Регистрация" } },
      {
        path: "login/yandex",
        element: <YandexCallbackPage />,
        handle: { crumb: "Яндекс ID" },
      },
      {
        path: "learn",
        handle: { crumb: "Обучение" },
        children: [
          { index: true, element: <TracksPage /> },
          {
            path: ":track",
            handle: { crumb: trackCrumb },
            children: [
              { index: true, element: <TrackPage /> },
              {
                path: ":lesson",
                element: <LessonPage />,
                handle: { crumb: lessonCrumb },
              },
            ],
          },
        ],
      },
      { path: "*", element: <NotFoundPage />, handle: { crumb: "Страница не найдена" } },
    ],
  },
]);
