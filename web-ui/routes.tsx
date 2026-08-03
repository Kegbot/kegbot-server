import { Route, Routes } from "react-router";
import { MainLayout } from "@/layout/main-layout";
import { HomeView } from "@/views/home-view";

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route path="/" element={<HomeView />} />
      </Route>
    </Routes>
  );
}
