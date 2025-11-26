import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "NFTables Analyzer",
  description: "Visualize and analyze nftables rules",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
