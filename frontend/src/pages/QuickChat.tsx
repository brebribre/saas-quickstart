import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Send, Loader2 } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { apiPost } from "@/utils/api";

// Available models for selection
const AVAILABLE_MODELS = [
  { id: "gpt-3.5-turbo", name: "GPT-3.5 Turbo" },
  { id: "gpt-4", name: "GPT-4" },
  { id: "claude-3-opus", name: "Claude 3 Opus" },
  { id: "claude-3-sonnet", name: "Claude 3 Sonnet" },
  { id: "gemini-pro", name: "Gemini Pro" }
];

const QuickChat = () => {
  const { toast } = useToast();
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [selectedModel, setSelectedModel] = useState(AVAILABLE_MODELS[0].id);
  const [isLoading, setIsLoading] = useState(false);
  const [chatHistory, setChatHistory] = useState<Array<{ question: string; answer: string }>>([]);

  const handleModelChange = (value: string) => {
    setSelectedModel(value);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!question.trim()) {
      toast({
        title: "Empty Question",
        description: "Please enter a question to continue.",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    setAnswer('');

    try {
      const data = await apiPost('ask', {
        question,
        model: selectedModel
      });
      
      setAnswer(data.answer);
      
      // Add to chat history
      setChatHistory(prev => [...prev, { 
        question, 
        answer: data.answer 
      }]);
      
      // Clear question input
      setQuestion('');
    } catch (error) {
      console.error('Error fetching answer:', error);
      toast({
        title: "Error",
        description: "Failed to get an answer. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto max-w-4xl">
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Quick Chat</CardTitle>
          <CardDescription>
            Ask any question and get an instant answer from AI
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label htmlFor="model-select" className="text-sm font-medium">
                  Select AI Model
                </label>
                <Select value={selectedModel} onValueChange={handleModelChange}>
                  <SelectTrigger className="w-[200px]">
                    <SelectValue placeholder="Select a model" />
                  </SelectTrigger>
                  <SelectContent>
                    {AVAILABLE_MODELS.map((model) => (
                      <SelectItem key={model.id} value={model.id}>
                        {model.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              
              <div className="flex space-x-2">
                <Input
                  id="question"
                  placeholder="Type your question here..."
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  disabled={isLoading}
                  className="flex-1"
                />
                <Button type="submit" disabled={isLoading || !question.trim()}>
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                  <span className="ml-2">Ask</span>
                </Button>
              </div>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Answer display */}
      {answer && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg">Answer</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="whitespace-pre-wrap">{answer}</div>
          </CardContent>
        </Card>
      )}

      {/* Chat history */}
      {chatHistory.length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-bold">Chat History</h2>
          {chatHistory.map((chat, index) => (
            <Card key={index} className="mb-4">
              <CardHeader className="py-3">
                <CardTitle className="text-sm font-medium">Question</CardTitle>
              </CardHeader>
              <CardContent className="py-2">
                <p>{chat.question}</p>
              </CardContent>
              <CardHeader className="py-3 border-t">
                <CardTitle className="text-sm font-medium">Answer</CardTitle>
              </CardHeader>
              <CardContent className="py-2">
                <p className="whitespace-pre-wrap">{chat.answer}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};

export default QuickChat; 