"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { auth } from "@/lib/firebase";
import { createUserWithEmailAndPassword, signInWithEmailAndPassword, GoogleAuthProvider, signInWithPopup } from "firebase/auth";
import { useToast } from "@/hooks/use-toast";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LoginForm } from "@/components/login-form";
import { Toaster } from "@/components/ui/toaster";
import { db } from "@/lib/firebase";
import { doc, getDoc, setDoc } from "firebase/firestore";

export default function LoginPage() {
  const router = useRouter();
  const { toast } = useToast();
  const [isSignUp, setIsSignUp] = useState(false);

  const toggleMode = () => setIsSignUp(prev => !prev);

  const handleEmailSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const email = formData.get("email") as string;
    const password = formData.get("password") as string;
    try {
      if (isSignUp) {
        const cred = await createUserWithEmailAndPassword(auth, email, password);
        await setDoc(doc(db, "users", cred.user.uid), { credits: 3, email: email });
        toast({ title: "Account created successfully." });
      } else {
        const loginCred = await signInWithEmailAndPassword(auth, email, password);
        const userRef = doc(db, "users", loginCred.user.uid);
        const userSnap = await getDoc(userRef);
        if (!userSnap.exists()) {
          await setDoc(userRef, { credits: 3, email: email });
        }
        toast({ title: "Logged in successfully." });
      }
      router.replace("/");
    } catch (err) {
      console.error(err);
      toast({
        title: "Authentication error",
        description: err instanceof Error ? err.message : String(err),
        variant: "destructive",
      });
    }
  };

  const handleGoogleSignIn = async () => {
    const provider = new GoogleAuthProvider();
    try {
      await signInWithPopup(auth, provider);
      router.replace("/");
    } catch (err) {
      console.error(err);
      toast({
        title: "Google sign-in error",
        description: err instanceof Error ? err.message : String(err),
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen bg-grid bg-[#111111] flex flex-col">
      <main className="flex flex-1 items-center justify-center px-4 flex-col">
        <span className="text-xl max-w-[26rem] w-full text-left mb-8 font-bold">Notebook Maker</span>
        <Card className="w-full max-w-[26rem] shadow-lg border-gray-200 dark:border-[#262626] bg-white/90 dark:bg-[#111111]/90 backdrop-blur-sm">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl font-bold text-center text-gray-900 dark:text-[#FAFAFA]">
              {isSignUp ? "Sign Up" : "Login"}
            </CardTitle>
            <CardDescription className="text-center text-gray-500 dark:text-gray-400">
              {isSignUp ? "Create your account" : "Enter your credentials to access your account"}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <LoginForm
              onSubmit={handleEmailSubmit}
              isSignUp={isSignUp}
              onToggleMode={toggleMode}
              onGoogleSignIn={handleGoogleSignIn}
            />
          </CardContent>
        </Card>
      </main>
      <Toaster />
    </div>
  );
}
