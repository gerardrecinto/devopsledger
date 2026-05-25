import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "DevOpsLedger",
  description: "Operational memory layer for GitOps teams",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
