import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";

const AuthCallback = () => {
  const navigate = useNavigate();
  const { isLoggedIn } = useAuth();

  useEffect(() => {
    // Check if the user is logged in
    if (isLoggedIn) {
      toast.success("Login successful", {
        description: "Welcome back!"
      });
      navigate("/dashboard");
    } else {
      // If not logged in, redirect to login page
      toast.error("Authentication failed", {
        description: "Please try again."
      });
      navigate("/login");
    }
  }, [isLoggedIn, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h2 className="text-2xl font-bold mb-2">Processing authentication...</h2>
        <p className="text-muted-foreground">Please wait while we complete your login.</p>
      </div>
    </div>
  );
};

export default AuthCallback; 