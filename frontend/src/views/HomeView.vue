<script setup lang="ts">
// Inbox view component
import HomeNavbar from '@/components/HomeNavbar.vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card'
import { 
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger
} from '@/components/ui/accordion'
import { 
  Bot, 
  BookOpen, 
  LineChart, 
  Layers, 
  Settings, 
  BarChart, 
  CheckCircle2, 
  ArrowRight,
  Users,
  Rocket,
  Database,
  Shield,
  Search,
  FileUp,
  ExternalLink,
  MessageSquare,
  Wrench,
  FileText
} from 'lucide-vue-next'

const router = useRouter()
const authStore = useAuthStore()

const navigateToLogin = () => {
  router.push('/login')
}

const navigateToRegister = () => {
  router.push('/register')
}

const navigateToDashboard = () => {
  router.push('/app')
}

const testimonials = [
  {
    name: 'Sarah Johnson',
    role: 'Marketing Director',
    company: 'TechCorp',
    quote: 'This platform has transformed how we manage our workflows. Productivity has increased by 40% since we started using it.',
  },
  {
    name: 'Michael Chen',
    role: 'CTO',
    company: 'Startup Innovations',
    quote: 'The integration capabilities are unmatched. We were able to connect all our existing tools without any hassle.',
  },
  {
    name: 'Priya Patel',
    role: 'Operations Lead',
    company: 'Global Solutions',
    quote: 'Our team can focus on strategic work now that repetitive tasks are automated. Wish we had discovered this sooner!',
  },
  {
    name: 'Robert Garcia',
    role: 'Sales Manager',
    company: 'Enterprise Inc.',
    quote: 'The analytics tools have given us insights we never had before, directly increasing our conversion rates.',
  }
]

const faqs = [
  {
    question: 'How do I get started?',
    answer: 'Getting started is simple! Just create an account, and our onboarding wizard will guide you through setting up your first project. You can be up and running in minutes.'
  },
  {
    question: 'Is there a free plan available?',
    answer: 'Yes, we offer a generous free tier that includes all essential features. You can use this indefinitely with limitations on usage volumes. Paid plans remove these restrictions and add premium features.'
  },
  {
    question: 'Can I integrate with my existing tools?',
    answer: 'Absolutely! Our platform offers seamless integration with most popular business tools and services through our API and pre-built connectors. Custom integrations are also supported.'
  },
  {
    question: 'What kind of support is available?',
    answer: 'All plans include access to our comprehensive documentation and community forums. Paid plans additionally offer email support, while our Enterprise tier includes dedicated account management and priority support.'
  },
  {
    question: 'Is my data secure?',
    answer: 'Security is our top priority. We use industry-standard encryption, regular security audits, and comply with GDPR and SOC 2 requirements. Your data remains private and is never used for training purposes.'
  }
]

const features = [
  {
    title: 'AI-Powered Automation',
    description: 'Leverage advanced AI to automate routine tasks and free your team for strategic work.',
    icon: Bot
  },
  {
    title: 'Seamless Integrations',
    description: 'Connect with your existing tools and platforms for a unified workflow experience.',
    icon: Settings
  },
  {
    title: 'Advanced Analytics',
    description: 'Gain valuable insights with comprehensive reporting and visualization tools.',
    icon: BarChart
  },
  {
    title: 'Customizable Workflows',
    description: 'Create workflows that match exactly how your business operates with our flexible platform.',
    icon: Layers
  },
  {
    title: 'Team Collaboration',
    description: 'Enhance team productivity with real-time collaboration and communication tools.',
    icon: Users
  },
  {
    title: 'Comprehensive Documentation',
    description: 'Get started quickly with extensive guides, tutorials, and examples.',
    icon: BookOpen
  }
]

const plans = [
  {
    name: 'Free',
    price: '$0',
    billing: 'Forever free',
    description: 'Perfect for individuals and small projects',
    features: [
      'Access to core platform',
      'Basic automation features',
      'Up to 3 projects',
      'Community support',
      '1GB storage'
    ],
    cta: 'Get Started',
    variant: 'outline' as const
  },
  {
    name: 'Pro',
    price: '$29',
    billing: 'per month',
    description: 'Ideal for professionals and growing teams',
    features: [
      'Everything in Free',
      'Advanced automations',
      'Unlimited projects',
      'Priority email support',
      '25GB storage',
      'API access'
    ],
    cta: 'Start Free Trial',
    variant: 'default' as const,
    popular: true
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    billing: 'Contact for pricing',
    description: 'Tailored solutions for large organizations',
    features: [
      'Everything in Pro',
      'Custom integrations',
      'Dedicated account manager',
      'SLA guarantees',
      'Unlimited storage',
      'Advanced security features'
    ],
    cta: 'Contact Sales',
    variant: 'secondary' as const
  }
]

const securityFeatures = [
  {
    title: 'Data Encryption',
    description: 'AES-256 encryption for data at rest and TLS for data in transit',
    icon: Shield
  },
  {
    title: 'Compliance Ready',
    description: 'SOC 2 Type II certified and GDPR compliant',
    icon: CheckCircle2
  },
  {
    title: 'Data Ownership',
    description: 'Your data remains yours - we never train models on your content',
    icon: Database
  }
]

const pressFeatures = [
  { name: 'TechCrunch', logo: 'techcrunch.svg' },
  { name: 'Forbes', logo: 'forbes.svg' },
  { name: 'Wired', logo: 'wired.svg' },
  { name: 'Bloomberg', logo: 'bloomberg.svg' }
]

const aiTools = [
  {
    title: 'Connect Google Drive',
    description: 'Link your Google Drive to extract insights from documents, spreadsheets, and presentations automatically.',
    icon: ExternalLink
  },
  {
    title: 'Upload Files Directly',
    description: 'Drag and drop documents, PDFs, and images to have the AI analyze and extract valuable information.',
    icon: FileUp
  },
  {
    title: 'Web Search Integration',
    description: 'Let the AI search the web to find the most up-to-date information for your queries and projects.',
    icon: Search
  }
]

const agentFeatures = [
  {
    title: 'Customize Your AI Agents',
    description: 'Create specialized AI agents with specific tools and knowledge tailored to your exact needs.',
    icon: Bot
  },
  {
    title: 'Assign Specific Tools',
    description: 'Equip your agents with the right tools like web search, file processing, or custom integrations.',
    icon: Wrench
  },
  {
    title: 'Define Clear Job Descriptions',
    description: 'Set precise job descriptions so your agents know exactly what tasks they need to handle.',
    icon: FileText
  },
  {
    title: 'Natural Conversations',
    description: 'Interact with your agents using natural language to get answers, insights, and assistance.',
    icon: MessageSquare
  }
]
</script>

<template>
  <div class="min-h-screen flex flex-col">
    <HomeNavbar />
    
    <main class="flex-1 flex flex-col">
      <!-- Hero Section -->
      <section class="py-20 px-6 flex flex-col items-center justify-center text-center bg-gradient-to-b from-background to-muted/30">
        <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">
          Build Better, Work Smarter
        </h1>
        <p class="text-lg md:text-xl text-muted-foreground max-w-3xl mb-10">
          The intelligent platform that transforms how teams work. Automate repetitive tasks, 
          gain valuable insights, and focus on what really matters.
        </p>
        
        <div class="flex flex-col sm:flex-row gap-4">
          <Button 
            v-if="authStore.isAuthenticated"
            @click="navigateToDashboard" 
            size="lg"
            class="text-lg"
          >
            Go to Dashboard
          </Button>
          <template v-else>
            <Button 
              @click="navigateToLogin" 
              size="lg"
              class="text-lg"
            >
              Get Started
            </Button>
            <Button 
              @click="navigateToRegister" 
              variant="outline"
              size="lg"
              class="text-lg"
            >
              Learn More
            </Button>
          </template>
        </div>
      </section>
      
      <!-- Custom AI Agents Section -->
      <section class="py-16 px-6">
        <div class="max-w-7xl mx-auto">
          <div class="text-center mb-16">
            <h2 class="text-3xl font-bold mb-4">Create Your Own AI Agents</h2>
            <p class="text-xl text-muted-foreground max-w-3xl mx-auto">
              Build specialized AI assistants that understand your business and handle specific tasks
            </p>
          </div>
          
          <div class="grid md:grid-cols-2 gap-12 mb-12">
            <div>
              <h3 class="text-2xl font-semibold mb-4">Your Personal AI Workforce</h3>
              <p class="text-muted-foreground mb-6">
                Create customized AI agents that can answer questions, perform tasks, and manage workflows
                based on the specific tools and job descriptions you provide.
              </p>
              
              <ul class="space-y-4">
                <li v-for="(feature, index) in agentFeatures" :key="index" class="flex gap-3">
                  <component :is="feature.icon" class="h-6 w-6 text-primary flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 class="font-medium">{{ feature.title }}</h4>
                    <p class="text-sm text-muted-foreground">{{ feature.description }}</p>
                  </div>
                </li>
              </ul>
              
              <Button class="mt-8" variant="default">
                Learn More About AI Agents
              </Button>
            </div>
            
            <div class="bg-muted/30 rounded-lg p-6 border border-border">
              <h4 class="text-lg font-medium mb-3">Example: Research Assistant Agent</h4>
              
              <div class="space-y-3 mb-6">
                <div>
                  <h5 class="text-sm font-medium">Agent Name</h5>
                  <p class="text-muted-foreground text-sm bg-background/60 p-2 rounded">Research Assistant</p>
                </div>
                
                <div>
                  <h5 class="text-sm font-medium">Job Description</h5>
                  <p class="text-muted-foreground text-sm bg-background/60 p-2 rounded">
                    Help with market research, compile data from multiple sources, and summarize findings into concise reports.
                  </p>
                </div>
                
                <div>
                  <h5 class="text-sm font-medium">Assigned Tools</h5>
                  <div class="flex flex-wrap gap-2 mt-1">
                    <span class="inline-flex items-center rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-semibold text-primary">
                      <Search class="mr-1 h-3 w-3" /> Web Search
                    </span>
                    <span class="inline-flex items-center rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-semibold text-primary">
                      <FileUp class="mr-1 h-3 w-3" /> File Upload
                    </span>
                    <span class="inline-flex items-center rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-semibold text-primary">
                      <BarChart class="mr-1 h-3 w-3" /> Data Analysis
                    </span>
                  </div>
                </div>
              </div>
              
              <div class="border-t border-border pt-4">
                <h5 class="text-sm font-medium mb-2">Example Conversation</h5>
                <div class="space-y-3">
                  <div class="flex gap-2">
                    <div class="flex-shrink-0 w-6 h-6 rounded-full bg-background flex items-center justify-center">
                      <Users class="h-3 w-3" />
                    </div>
                    <p class="text-sm bg-background/60 rounded-r-lg rounded-bl-lg p-2 max-w-[80%]">
                      Can you research the current market trends for renewable energy in Europe?
                    </p>
                  </div>
                  <div class="flex gap-2 justify-end">
                    <p class="text-sm bg-primary/10 rounded-l-lg rounded-br-lg p-2 max-w-[80%]">
                      I'll search for the latest renewable energy trends in Europe and compile a summary report with data visualization. Would you like me to focus on any particular technology or country?
                    </p>
                    <div class="flex-shrink-0 w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center">
                      <Bot class="h-3 w-3" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
      
      <!-- Features Section -->
      <section class="py-16 px-6">
        <div class="max-w-7xl mx-auto">
          <div class="text-center mb-16">
            <h2 class="text-3xl font-bold mb-4">Powerful Features for Modern Teams</h2>
            <p class="text-xl text-muted-foreground max-w-3xl mx-auto">
              Everything you need to streamline workflows, enhance productivity, and drive results.
            </p>
          </div>
          
          <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card v-for="(feature, index) in features" :key="index" class="border-border/40 hover:border-primary/20 transition-colors">
              <CardHeader>
                <div class="flex items-center gap-2">
                  <component :is="feature.icon" class="h-5 w-5 text-primary" />
                  <CardTitle>{{ feature.title }}</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p class="text-muted-foreground">
                  {{ feature.description }}
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>
      
      <!-- Testimonials Section -->
      <section class="py-16 px-6">
        <div class="max-w-7xl mx-auto">
          <div class="text-center mb-16">
            <h2 class="text-3xl font-bold mb-4">What Our Users Say</h2>
            <p class="text-xl text-muted-foreground max-w-3xl mx-auto">
              Join thousands of teams who have transformed how they work
            </p>
          </div>
          
          <div class="grid md:grid-cols-2 gap-8">
            <Card v-for="(testimonial, index) in testimonials" :key="index" class="border-border/40">
              <CardContent class="pt-6">
                <p class="text-lg italic mb-6">
                  "{{ testimonial.quote }}"
                </p>
                <div class="flex items-center gap-2">
                  <div class="w-10 h-10 rounded-full bg-muted flex items-center justify-center">
                    {{ testimonial.name.charAt(0) }}
                  </div>
                  <div>
                    <p class="font-medium">{{ testimonial.name }}</p>
                    <p class="text-sm text-muted-foreground">{{ testimonial.role }}, {{ testimonial.company }}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>
      
      <!-- Pricing Section -->
      <section class="py-16 px-6 bg-muted/30">
        <div class="max-w-7xl mx-auto">
          <div class="text-center mb-16">
            <h2 class="text-3xl font-bold mb-4">Simple, Transparent Pricing</h2>
            <p class="text-xl text-muted-foreground max-w-3xl mx-auto">
              Choose the plan that's right for you and your team
            </p>
          </div>
          
          <div class="grid md:grid-cols-3 gap-8">
            <Card v-for="(plan, index) in plans" :key="index" 
              class="border-border/40 relative"
              :class="{'shadow-lg border-primary/50': plan.popular}"
            >
              <div v-if="plan.popular" class="absolute top-0 right-0 bg-primary text-primary-foreground px-3 py-1 text-xs rounded-bl-md rounded-tr-md font-medium">
                Popular
              </div>
              
              <CardHeader>
                <CardTitle>{{ plan.name }}</CardTitle>
                <div class="mt-2">
                  <span class="text-3xl font-bold">{{ plan.price }}</span>
                  <span class="text-muted-foreground"> {{ plan.billing }}</span>
                </div>
                <CardDescription class="mt-2">{{ plan.description }}</CardDescription>
              </CardHeader>
              
              <CardContent>
                <ul class="space-y-2">
                  <li v-for="(feature, featureIndex) in plan.features" :key="featureIndex" class="flex items-center gap-2">
                    <CheckCircle2 class="h-4 w-4 text-primary" />
                    <span>{{ feature }}</span>
                  </li>
                </ul>
              </CardContent>
              
              <CardFooter>
                <Button :variant="plan.variant" class="w-full">
                  {{ plan.cta }}
                </Button>
              </CardFooter>
            </Card>
          </div>
        </div>
      </section>
      
      <!-- AI Tools Section -->
      <section class="py-16 px-6 bg-muted/30">
        <div class="max-w-7xl mx-auto">
          <div class="text-center mb-16">
            <h2 class="text-3xl font-bold mb-4">Powerful AI Tools & Integrations</h2>
            <p class="text-xl text-muted-foreground max-w-3xl mx-auto">
              Connect your data sources and enhance your AI experience with these powerful integrations
            </p>
          </div>
          
          <div class="grid md:grid-cols-3 gap-8">
            <Card v-for="(tool, index) in aiTools" :key="index" class="border-border/40 hover:border-primary/20 transition-colors">
              <CardHeader>
                <div class="flex items-center gap-2">
                  <component :is="tool.icon" class="h-5 w-5 text-primary" />
                  <CardTitle>{{ tool.title }}</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p class="text-muted-foreground">
                  {{ tool.description }}
                </p>
              </CardContent>
              <CardFooter>
                <p class="text-sm text-muted-foreground">
                  The AI stores this in its knowledge base for answering your future questions.
                </p>
              </CardFooter>
            </Card>
          </div>
        </div>
      </section>
      
      <!-- FAQ Section -->
      <section class="py-16 px-6">
        <div class="max-w-3xl mx-auto">
          <div class="text-center mb-12">
            <h2 class="text-3xl font-bold mb-4">Frequently Asked Questions</h2>
            <p class="text-muted-foreground">
              Find answers to common questions about our platform.
            </p>
          </div>
          
          <Accordion type="single" collapsible class="w-full">
            <AccordionItem v-for="(faq, index) in faqs" :key="index" :value="`item-${index}`">
              <AccordionTrigger>{{ faq.question }}</AccordionTrigger>
              <AccordionContent>
                {{ faq.answer }}
              </AccordionContent>
            </AccordionItem>
          </Accordion>
        </div>
      </section>
      
      <!-- Final CTA Section -->
      <section class="py-20 px-6 bg-primary text-primary-foreground">
        <div class="max-w-4xl mx-auto text-center">
          <h2 class="text-3xl font-bold mb-4">Ready to Transform How Your Team Works?</h2>
          <p class="text-xl mb-8 text-primary-foreground/80">
            Join thousands of teams who are already working smarter, not harder.
          </p>
          
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              variant="secondary" 
              size="lg"
              class="text-lg"
              @click="navigateToRegister"
            >
              Start Free Trial
            </Button>
            <Button 
              variant="outline" 
              size="lg"
              class="text-lg text-primary-foreground border-primary-foreground/20 hover:bg-primary-foreground/10"
            >
              Schedule Demo
              <ArrowRight class="ml-2 h-5 w-5" />
            </Button>
          </div>
        </div>
      </section>
    </main>
    
    <footer class="py-12 px-6 bg-muted">
      <div class="max-w-7xl mx-auto">
        <div class="grid md:grid-cols-4 gap-8 mb-8">
          <div>
            <h3 class="font-bold mb-4">Product</h3>
            <ul class="space-y-2">
              <li><a href="#" class="text-muted-foreground hover:text-foreground">Features</a></li>
              <li><a href="#" class="text-muted-foreground hover:text-foreground">Integrations</a></li>
              <li><a href="#" class="text-muted-foreground hover:text-foreground">Pricing</a></li>
              <li><a href="#" class="text-muted-foreground hover:text-foreground">Enterprise</a></li>
            </ul>
          </div>
          
          <div>
            <h3 class="font-bold mb-4">Resources</h3>
            <ul class="space-y-2">
              <li><a href="#" class="text-muted-foreground hover:text-foreground">Documentation</a></li>
              <li><a href="#" class="text-muted-foreground hover:text-foreground">Guides</a></li>
              <li><a href="#" class="text-muted-foreground hover:text-foreground">Blog</a></li>
              <li><a href="#" class="text-muted-foreground hover:text-foreground">API Reference</a></li>
            </ul>
          </div>
          
          <div>
            <h3 class="font-bold mb-4">Company</h3>
            <ul class="space-y-2">
              <li><a href="#" class="text-muted-foreground hover:text-foreground">About</a></li>
              <li><a href="#" class="text-muted-foreground hover:text-foreground">Careers</a></li>
              <li><a href="#" class="text-muted-foreground hover:text-foreground">Contact</a></li>
              <li><a href="#" class="text-muted-foreground hover:text-foreground">Partners</a></li>
            </ul>
          </div>
          
          <div>
            <h3 class="font-bold mb-4">Legal</h3>
            <ul class="space-y-2">
              <li><a href="#" class="text-muted-foreground hover:text-foreground">Privacy Policy</a></li>
              <li><a href="#" class="text-muted-foreground hover:text-foreground">Terms of Service</a></li>
              <li><a href="#" class="text-muted-foreground hover:text-foreground">Security</a></li>
            </ul>
          </div>
        </div>
        
        <div class="border-t border-border pt-8 flex justify-between items-center flex-col md:flex-row gap-4">
          <div class="text-sm text-muted-foreground">
            © 2024 Your Company. All rights reserved.
          </div>
          <div class="flex space-x-6">
            <a href="#" class="text-muted-foreground hover:text-foreground">
              <span class="sr-only">Twitter</span>
              <!-- Icon would go here -->
            </a>
            <a href="#" class="text-muted-foreground hover:text-foreground">
              <span class="sr-only">LinkedIn</span>
              <!-- Icon would go here -->
            </a>
            <a href="#" class="text-muted-foreground hover:text-foreground">
              <span class="sr-only">GitHub</span>
              <!-- Icon would go here -->
            </a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* Add any component-specific styles here */
</style>
