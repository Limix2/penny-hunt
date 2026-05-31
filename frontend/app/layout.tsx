import "./globals.css";
import type { Metadata, Viewport } from "next";
import { BottomNav } from "@/components/BottomNav";
import { SWRegister } from "@/components/SWRegister";
import { PWAInstall } from "@/components/PWAInstall";
import { ThemeToggle } from "@/components/ThemeToggle";

export const metadata: Metadata = {
  title: "Penny Hunt",
  description: "Find penny items & deep clearance near you",
  manifest: "/manifest.json",
  appleWebApp: { capable: true, title: "Penny Hunt", statusBarStyle: "black-translucent" },
};
export const viewport: Viewport = {
  themeColor: "#4C3AFF", width: "device-width", initialScale: 1, maximumScale: 1,
};

const themeInit = `try{var t=localStorage.getItem('ph-theme');if(t==='dark'||(!t&&window.matchMedia('(prefers-color-scheme:dark)').matches)){document.documentElement.classList.add('dark')}}catch(e){}`;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head><script dangerouslySetInnerHTML={{ __html: themeInit }} /></head>
      <body className="font-sans min-h-screen pb-20">
        <SWRegister />
        <ThemeToggle />
        {children}
        <PWAInstall />
        <BottomNav />
      </body>
    </html>
  );
}
