import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useAuth } from "@/contexts/AuthContext";

const Dashboard = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div>
        <h1 className="mb-3 text-2xl font-bold">Dashboard</h1>
        <Card className="bg-gradient-to-r">
          <CardHeader>
            <CardTitle>Welcome{user?.name ? `, ${user.name}` : ""}!</CardTitle>
            <CardDescription>
              This is a simplified dashboard with a modern sidebar layout.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>

      {/* Content Section */}
      <div>
        <h2 className="mb-3 text-xl font-semibold">Dashboard Content</h2>
        <Card>
          <CardContent className="p-6">
            <p>This is a clean dashboard with a modern sidebar layout.</p>
            <p className="mt-2">You can use all shadcn components with Tailwind CSS in this project.</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
