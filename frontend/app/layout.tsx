import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import ClientProviders from "../components/ClientProviders";
import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import CartDrawer from "../components/CartDrawer";
import AIShoppingAssistant from "../components/AIShoppingAssistant";
import ProductComparisonBar from "../components/ProductComparisonBar";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "AJIO | Online Shopping for Fashion, Footwear, Tech & Lifestyle",
  description: "Shop online for men, women & kids apparel, footwear, beauty, watches and electronics with AI-driven personalized recommendations and 100% Cash on Delivery.",
  keywords: ["AJIO", "Fashion", "Footwear", "Online Shopping", "COD", "Cash on Delivery", "Personalized Recommendations"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="light">
      <body className={`${inter.variable} font-sans bg-background text-foreground min-h-screen flex flex-col antialiased selection:bg-orange-500 selection:text-white transition-colors duration-400`}>
        <ClientProviders>
          <div className="flex flex-col min-h-screen">
            <Navbar />
            <CartDrawer />
            <AIShoppingAssistant />
            <ProductComparisonBar />
            <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
              {children}
            </main>
            <Footer />
          </div>
        </ClientProviders>
      </body>
    </html>
  );
}

