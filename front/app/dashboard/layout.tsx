import type { Metadata } from "next";
import Providers from "../Providers";

export const metadata: Metadata = {
  title: "Dashboard",
  description: "Your task management dashboard",
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}