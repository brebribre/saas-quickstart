import React from 'react';
import { Link } from 'react-router-dom';

const AuthNavbar: React.FC = () => {
  return (
    <div className="md:hidden w-full bg-background border-b py-3 px-4">
      <div className="flex items-center justify-center">
        <Link to="/" className="flex items-center">
          <span className="text-2xl font-bold font-league-spartan tracking-tight">stratigo</span>
        </Link>
      </div>
    </div>
  );
};

export default AuthNavbar; 