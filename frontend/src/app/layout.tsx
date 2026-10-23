import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "StockSense AI | Educational Indian Equity Direction Predictor",
  description: "A private student project for transparently exploring next-session stock direction.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="font-sans antialiased bg-[#0B0F1A] text-[#F1F5FF] selection:bg-[#6EE7C2]/30 selection:text-[#6EE7C2]">
        {children}
      </body>
    </html>
  );
}
