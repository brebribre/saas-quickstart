import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { useTheme } from "@/contexts/ThemeContext";
import { toast } from "sonner";
import Layout from "@/components/layout/Layout";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { User, Upload, FileText, X, Download } from "lucide-react";
import { cn } from "@/lib/utils";

const Profile = () => {
  const { user, isLoggedIn } = useAuth();
  const { theme } = useTheme();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  
  // Profile form state
  const [formData, setFormData] = useState({
    fullName: user?.name || "",
    jobTitle: "",
    company: "",
    bio: "",
    location: "",
    website: "",
    github: "",
    linkedin: "",
    twitter: "",
    skills: "",
    experience: "0-1"
  });

  // Custom button class based on theme
  const saveButtonClass = theme === 'dark' 
    ? "bg-white text-black hover:bg-white/90" 
    : "bg-black text-white hover:bg-black/90";

  // Custom input class for consistent theming
  const inputClass = "bg-[hsl(var(--background))] border-[hsl(var(--border))] focus:ring-[hsl(var(--ring))] focus:border-[hsl(var(--ring))] placeholder:text-[hsl(var(--muted-foreground))]";
  const selectTriggerClass = "bg-[hsl(var(--background))] border-[hsl(var(--border))] data-[placeholder]:text-[hsl(var(--muted-foreground))]";

  useEffect(() => {
    // Redirect to login if not logged in
    if (!isLoggedIn) {
      navigate("/login");
    }
    
    // Update form data when user changes
    if (user) {
      setFormData(prev => ({
        ...prev,
        fullName: user.name || prev.fullName
      }));
    }
  }, [isLoggedIn, navigate, user]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSelectChange = (name: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Check file type
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    if (!allowedTypes.includes(file.type)) {
      toast.error("Invalid file type", {
        description: "Please upload a PDF or Word document (DOC/DOCX)."
      });
      return;
    }

    // Check file size (5MB limit)
    const maxSize = 5 * 1024 * 1024; // 5MB in bytes
    if (file.size > maxSize) {
      toast.error("File too large", {
        description: "Please upload a file smaller than 5MB."
      });
      return;
    }

    setResumeFile(file);
    toast.success("Resume uploaded", {
      description: "Your resume has been uploaded successfully."
    });
  };

  const removeResume = () => {
    setResumeFile(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      // Here you would typically call an API to update the user's profile
      // For now, we'll just simulate a successful update
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      toast.success("Profile updated", {
        description: "Your profile has been successfully updated."
      });
    } catch (error) {
      toast.error("Failed to update profile", {
        description: "Please try again later."
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Get user initials for avatar
  const userInitial = user?.name ? user.name.charAt(0).toUpperCase() : "U";

  return (
    <Layout>
      <div className="container mx-auto py-8 px-4">
        <h1 className="text-3xl font-bold mb-6">Your Profile</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Profile Summary Card */}
          <Card>
            <CardHeader className="text-center">
            <div className="flex justify-center mb-4">
                <Avatar className="h-24 w-24">
                  <AvatarFallback className="text-xl bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]">
                    {userInitial}
                  </AvatarFallback>
                </Avatar>
              </div>
              <CardTitle>{user?.name || "Your Name"}</CardTitle>
              <CardDescription>{user?.email || "your.email@example.com"}</CardDescription>
            </CardHeader>
            <CardContent className="text-center">
              <p className="text-sm text-muted-foreground">
                Complete your profile to help us personalize your experience.
              </p>
            </CardContent>
          </Card>
          
          {/* Profile Edit Form */}
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle>Edit Profile</CardTitle>
              <CardDescription>
                Update your profile information to help us personalize your experience.
            </CardDescription>
          </CardHeader>
            <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="fullName">Full Name</Label>
                  <Input
                    id="fullName"
                    name="fullName"
                    value={formData.fullName}
                    onChange={handleChange}
                    placeholder="John Doe"
                    className={inputClass}
                  />
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="jobTitle">Job Title</Label>
                    <Input
                      id="jobTitle"
                      name="jobTitle"
                      value={formData.jobTitle}
                      onChange={handleChange}
                      placeholder="Software Engineer"
                      className={inputClass}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="company">Company</Label>
                    <Input
                      id="company"
                      name="company"
                      value={formData.company}
                      onChange={handleChange}
                      placeholder="Acme Inc."
                      className={inputClass}
                    />
                  </div>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="bio">Bio</Label>
                  <Textarea
                    id="bio"
                    name="bio"
                    value={formData.bio}
                    onChange={handleChange}
                    placeholder="Tell us about yourself..."
                    rows={4}
                    className={inputClass}
                  />
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="location">Location</Label>
                    <Input
                      id="location"
                      name="location"
                      value={formData.location}
                      onChange={handleChange}
                      placeholder="San Francisco, CA"
                      className={inputClass}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="website">Website</Label>
                    <Input
                      id="website"
                      name="website"
                      value={formData.website}
                      onChange={handleChange}
                      placeholder="https://yourwebsite.com"
                      className={inputClass}
                    />
              </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="github">GitHub</Label>
                    <Input
                      id="github"
                      name="github"
                      value={formData.github}
                      onChange={handleChange}
                      placeholder="username"
                      className={inputClass}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="linkedin">LinkedIn</Label>
                    <Input
                      id="linkedin"
                      name="linkedin"
                      value={formData.linkedin}
                      onChange={handleChange}
                      placeholder="username"
                      className={inputClass}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="twitter">Twitter</Label>
                    <Input
                      id="twitter"
                      name="twitter"
                      value={formData.twitter}
                      onChange={handleChange}
                      placeholder="username"
                      className={inputClass}
                    />
              </div>
            </div>

                <div className="space-y-2">
                  <Label htmlFor="skills">Skills (comma separated)</Label>
                  <Input
                    id="skills"
                    name="skills"
                    value={formData.skills}
                    onChange={handleChange}
                    placeholder="React, TypeScript, Node.js"
                    className={inputClass}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="experience">Years of Experience</Label>
                  <Select
                    value={formData.experience}
                    onValueChange={(value) => handleSelectChange("experience", value)}
                  >
                    <SelectTrigger className={selectTriggerClass}>
                      <SelectValue placeholder="Select experience" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="0-1">0-1 years</SelectItem>
                      <SelectItem value="1-3">1-3 years</SelectItem>
                      <SelectItem value="3-5">3-5 years</SelectItem>
                      <SelectItem value="5-10">5-10 years</SelectItem>
                      <SelectItem value="10+">10+ years</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Resume Upload Section */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                    <Label>Resume</Label>
                    {resumeFile && (
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        className="h-auto p-0 text-muted-foreground hover:text-foreground"
                        onClick={removeResume}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                  
                  {resumeFile ? (
                    <div className="flex items-center justify-between rounded-lg border border-[hsl(var(--border))] p-4 bg-[hsl(var(--background))]">
                      <div className="flex items-center gap-2">
                        <FileText className="h-8 w-8 text-[hsl(var(--primary))]" />
                        <div>
                          <p className="text-sm font-medium">{resumeFile.name}</p>
                          <p className="text-xs text-[hsl(var(--muted-foreground))]">
                            {(resumeFile.size / (1024 * 1024)).toFixed(2)} MB
                  </p>
                </div>
                      </div>
                      <Button type="button" variant="outline" size="sm" className="ml-4">
                        <Download className="h-4 w-4 mr-2" />
                        Download
                      </Button>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-[hsl(var(--border))] p-8 bg-[hsl(var(--background))]">
                      <div className="flex flex-col items-center justify-center text-center">
                        <Upload className="h-8 w-8 text-[hsl(var(--muted-foreground))] mb-4" />
                        <p className="text-sm font-medium mb-1">
                          Drag and drop your resume here
                        </p>
                        <p className="text-xs text-[hsl(var(--muted-foreground))] mb-4">
                          PDF, DOC, or DOCX (max 5MB)
                        </p>
                        <Label
                          htmlFor="resume-upload"
                          className="cursor-pointer inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] shadow hover:bg-[hsl(var(--primary))]/90 h-9 px-4 py-2"
                        >
                          Choose File
                        </Label>
                        <Input
                          id="resume-upload"
                          type="file"
                          className="hidden"
                          accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                          onChange={handleFileChange}
                        />
                      </div>
              </div>
                  )}
            </div>
          </CardContent>
          <CardFooter>
            <Button 
                  type="submit" 
                  disabled={isLoading}
                  className={cn("w-full transition-colors", saveButtonClass)}
                >
                  {isLoading ? "Saving..." : "Save Profile"}
            </Button>
          </CardFooter>
            </form>
        </Card>
        </div>
      </div>
    </Layout>
  );
};

export default Profile;