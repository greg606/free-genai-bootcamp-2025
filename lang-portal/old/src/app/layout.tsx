import type React from "react"
import { Inter } from "next/font/google"
import "./globals.css"
import { ThemeProvider } from "@/components/theme-provider"
import { Sidebar } from "@/components/sidebar"
import { Breadcrumbs } from "@/components/breadcrumbs"

const inter = Inter({ subsets: ["latin"] })

export const metadata = {
  title: "German Language Learning App",
  description: "Learn German with interactive study activities and word management",
}

export default function RootLayout({
                                     children,
                                   }: {
  children: React.ReactNode
}) {
  return (
      <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
      <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
          suppressHydrationWarning
      >
        <div className="flex h-screen">
          <Sidebar />
          <div className="flex-1 flex flex-col overflow-hidden">
            <Breadcrumbs />
            <main className="flex-1 overflow-y-auto p-4">{children}</main>
          </div>
        </div>
      </ThemeProvider>
      </body>
      </html>
  )
}


