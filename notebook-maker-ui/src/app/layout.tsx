import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Script from "next/script";
import { SidebarWrapper } from "@/components/SidebarWrapper";
import { Analytics } from "@vercel/analytics/next";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Dopamine Maxeur",
  description: "Dopamine Maxeur",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <head>
        <Script src="/game/MIDIFile.js" strategy="beforeInteractive" />
        <Script src="/game/WebAudioFontPlayer.js" strategy="beforeInteractive" />
      </head>
      <body className={`${geistSans.variable} ${geistMono.variable} bg-background text-foreground`}>
        <SidebarWrapper>
          {children}
        </SidebarWrapper>
        <Analytics />
      </body>
    </html>
  );
}
