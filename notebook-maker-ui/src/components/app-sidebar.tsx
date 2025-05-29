"use client";
import * as React from "react"
import { useRouter } from "next/navigation";
import { signOut, onAuthStateChanged, type User } from "firebase/auth";
import { auth, db } from "@/lib/firebase";
import { doc, getDoc } from "firebase/firestore";
import Link from "next/link";

import {
  Sidebar,
  SidebarHeader,
  SidebarContent,
  SidebarFooter,
  SidebarSeparator,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarRail,
} from "@/components/ui/sidebar";
import { Home, ArrowUpRight, Minus, ChevronDown, Pen } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  const router = useRouter();
  const [user, setUser] = React.useState<User | null>(null);
  const [credits, setCredits] = React.useState<number | null>(null);
  React.useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (u) => {
      setUser(u);
      if (u) {
        const userRef = doc(db, "users", u.uid);
        getDoc(userRef)
          .then(snap => {
            if (snap.exists()) {
              const data = snap.data() as { credits: number };
              setCredits(data.credits);
            }
          })
          .catch(error => console.error("Failed to fetch credits:", error));
      } else {
        setCredits(null);
      }
    });
    return unsubscribe;
  }, []);
  const userName = user ? (user.displayName || (user.email ? user.email.split("@")[0] : "")) : "Guest";
  const handleLogout = async () => {
    await signOut(auth);
    router.replace("/login");
  };
  return (
    <Sidebar {...props}>
      <SidebarHeader>
        <div className="px-2 py-6 flex items-center">
          <span className="text-lg font-bold">Notebook Maker</span>
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarMenu className="px-4">
          <SidebarMenuItem>
            <SidebarMenuButton asChild size="lg">
              <Link href="/" className="border border-dashed border-gray-600 rounded-xl flex items-center justify-center">
                <Home className="w-8 h-8"/>
                <span className="text-lg">Dashboard</span>
              </Link>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarContent>

      <SidebarFooter>
        <SidebarSeparator />
        <SidebarGroup>
          <SidebarGroupLabel>Recent</SidebarGroupLabel>
          <SidebarGroupContent>
            <div className="px-3 py-2 text-sm text-muted-foreground">
              No recent items
            </div>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarSeparator />

        <SidebarGroup>
          <SidebarGroupLabel>Help and Tools</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <Link href="/feedback">
                    <ArrowUpRight className="mr-2" />
                    Feedback
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton asChild>
                  <Link href="/quick-guide">
                    <Minus className="mr-2" />
                    Quick guide
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
        <SidebarSeparator />
        <div className="px-4 py-2">
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="w-full flex items-center justify-between px-2 py-1 rounded-md hover:bg-muted">
                <span>{userName}</span>
                <ChevronDown className="w-4 h-4" />
              </button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {user ? (
                <>
                  <DropdownMenuItem disabled>
                    Crédits : {credits ?? 0}
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onSelect={() => router.push('/profile/edit')}>
                    <Pen className="mr-2 w-4 h-4" />
                    Edit Profile
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onSelect={handleLogout} className="text-destructive">
                    Logout
                  </DropdownMenuItem>
                </>
              ) : (
                <DropdownMenuItem onSelect={() => router.push('/login')}>
                  <ArrowUpRight className="mr-2" />
                  Login
                </DropdownMenuItem>
              )}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </SidebarFooter>

      <SidebarRail />
    </Sidebar>
  );
}
