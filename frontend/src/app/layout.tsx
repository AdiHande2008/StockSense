import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "StockSense AI | Educational stock-direction project",
  description: "A private student project for transparently exploring next-session stock direction.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
