import { Button } from "@/components/ui/button";
import Layout from "@/components/layout/Layout";
import { useLocation } from "react-router-dom";
import { useEffect } from "react";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname
    );
  }, [location.pathname]);

  return (
    <Layout>
      <div className="flex min-h-[60vh] flex-col items-center justify-center text-center">
        <h1 className="text-8xl font-bold tracking-tighter">404</h1>
        <p className="mt-4 text-xl text-muted-foreground">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <Button className="mt-8" asChild>
          <a href="/">Return to Home</a>
        </Button>
      </div>
    </Layout>
  );
};

export default NotFound;
