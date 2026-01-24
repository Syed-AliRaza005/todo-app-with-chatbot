import type { Metadata } from "next";
import { PublicProviders } from "../Providers";

export const metadata: Metadata = {
  title: "Todo App - Home",
  description: "A modern task management application",
};

export default function LandingPageLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <PublicProviders>
          {children}
        </PublicProviders>
      </body>
    </html>
  );
}