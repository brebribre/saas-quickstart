import React from 'react';
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Layout from "@/components/layout/Layout";
import { useAuth } from "@/contexts/AuthContext";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ToastTest } from "@/components/ToastTest";

const Dashboard = () => {
  const { isLoggedIn, user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (!isLoggedIn) {
      navigate("/login");
    }
  }, [isLoggedIn, navigate]);

  return (
    <Layout>
      <div className="space-y-6">
        {/* Welcome Section */}
        <div>
          <h1 className="mb-3 text-2xl font-bold">Dashboard</h1>
          <Card className="bg-gradient-to-r">
            <CardHeader>
              <CardTitle>Welcome{user?.name ? `, ${user.name}` : ""}!</CardTitle>
              <CardDescription>
                This is a simplified dashboard with a modern navbar layout.
              </CardDescription>
            </CardHeader>
          </Card>
        </div>

      

        {/* Content Section */}
        <div>
          <h2 className="mb-3 text-xl font-semibold">Dashboard Content</h2>
          <Card>
            <CardContent className="p-6">
              <p>This is a clean dashboard with a modern navbar layout.</p>
              <p className="mt-2">You can use all shadcn components with Tailwind CSS in this project.</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </Layout>
  );
};

export default Dashboard;
