<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Check, Circle, Dot, Plus, X } from 'lucide-vue-next';
import type { CreateAgentData } from '@/hooks/useAgents';
import { useAgents } from '@/hooks/useAgents';
import { useAuthStore } from '@/stores/auth';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/components/ui/toast/use-toast';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Stepper,
  StepperDescription,
  StepperItem,
  StepperSeparator,
  StepperTitle,
  StepperTrigger,
} from '@/components/ui/stepper';
import { useLangchain } from '@/hooks/useLangchain';

const router = useRouter();
const { createAgent } = useAgents();
const { getModels, getTools } = useLangchain();
const { user } = useAuthStore();
const { toast } = useToast();
const currentStep = ref(0);
const selectedTool = ref('');

const formData = ref<CreateAgentData>({
  name: '',
  description: '',
  model_id: '',
  user_id: user?.id || '',
  tool_categories: [],
  custom_instructions: '',
  configuration: {},
});

const availableModels = ref<{ id: string; name: string; provider: string; }[]>([]);
const loadingModels = ref(false);
const availableTools = ref<Record<string, { name: string; description: string; tools: { name: string; description: string; }[] }>>({});
const loadingTools = ref(false);

const loadModels = async () => {
  loadingModels.value = true;
  try {
    availableModels.value = await getModels();
  } catch (error) {
    toast({
      title: 'Error',
      description: 'Failed to load available models',
      variant: 'destructive',
    });
  } finally {
    loadingModels.value = false;
  }
};

const loadTools = async () => {
  loadingTools.value = true;
  try {
    availableTools.value = await getTools();
  } catch (error) {
    toast({
      title: 'Error',
      description: 'Failed to load available tools',
      variant: 'destructive',
    });
  } finally {
    loadingTools.value = false;
  }
};

// Load data when component mounts
onMounted(() => {
  loadModels();
  loadTools();
});

const isStepValid = computed(() => {
  switch (currentStep.value) {
    case 0: // Basic Info
      return formData.value.name.trim() !== '' && formData.value.model_id !== '';
    case 1: // Tools & Instructions
      return true; // Optional fields
    case 2: // Review
      return true;
    default:
      return false;
  }
});

const handleSubmit = async () => {
  try {
    const agent = await createAgent(formData.value);
    if (agent) {
      toast({
        title: 'Success',
        description: 'Agent created successfully',
      });
      router.push('/agents');
    }
  } catch (error) {
    toast({
      title: 'Error',
      description: 'Failed to create agent',
      variant: 'destructive',
    });
  }
};

const nextStep = () => {
  if (currentStep.value < 2) currentStep.value++;
};

const prevStep = () => {
  if (currentStep.value > 0) currentStep.value--;
};

const steps = [
  {
    step: 0,
    title: 'Basic Info',
    description: 'Name and model',
  },
  {
    step: 1,
    title: 'Capabilities',
    description: 'Tools and instructions',
  },
  {
    step: 2,
    title: 'Review',
    description: 'Confirm details',
  },
];

// Add watcher for selectedTool
watch(selectedTool, (newValue) => {
  if (newValue && !formData.value.tool_categories?.includes(newValue)) {
    formData.value.tool_categories = [...(formData.value.tool_categories || []), newValue];
    selectedTool.value = ''; // Reset selection
  }
});
</script>

<template>
  <div class="p-2">
    <div class="flex items-center gap-2 mb-6">
      <Button 
        variant="ghost" 
        size="icon"
        @click="router.push('/agents')"
      >
        <ArrowLeft class="h-4 w-4" />
      </Button>
      <h1 class="scroll-m-20 text-2xl font-bold tracking-tight">Create AI Agent</h1>
    </div>

    <div>
      <Stepper class="flex w-full items-start gap-2 mb-8">
        <StepperItem
          v-for="step in steps"
          :key="step.step"
          v-slot="{ state }"
          class="relative flex w-full flex-col items-center justify-center"
          :step="step.step"
        >
          <StepperSeparator
            v-if="step.step !== steps[steps.length - 1].step"
            class="absolute left-[calc(50%+20px)] right-[calc(-50%+10px)] top-5 block h-0.5 shrink-0 rounded-full bg-muted group-data-[state=completed]:bg-primary"
          />

          <StepperTrigger as-child>
            <Button
              :variant="state === 'completed' || state === 'active' ? 'default' : 'outline'"
              size="icon"
              class="z-10 rounded-full shrink-0"
              :class="[state === 'active' && 'ring-2 ring-ring ring-offset-2 ring-offset-background']"
            >
              <Check v-if="state === 'completed'" class="size-5" />
              <Circle v-if="state === 'active'" />
              <Dot v-if="state === 'inactive'" />
            </Button>
          </StepperTrigger>

          <div class="mt-5 flex flex-col items-center text-center">
            <StepperTitle
              :class="[state === 'active' && 'text-primary']"
              class="text-sm font-semibold transition lg:text-base"
            >
              {{ step.title }}
            </StepperTitle>
            <StepperDescription
              :class="[state === 'active' && 'text-primary']"
              class="sr-only text-xs text-muted-foreground transition md:not-sr-only lg:text-sm"
            >
              {{ step.description }}
            </StepperDescription>
          </div>
        </StepperItem>
      </Stepper>

      <!-- Step 1: Basic Info -->
      <div v-if="currentStep === 0">
        <Card>
          <CardContent class="pt-6 space-y-4">
            <div class="space-y-2">
              <Label for="name">Agent Name</Label>
              <Input 
                id="name"
                v-model="formData.name"
                placeholder="Enter agent name"
              />
            </div>

            <div class="space-y-2">
              <Label for="description">Description</Label>
              <Textarea
                id="description"
                v-model="formData.description"
                placeholder="Describe what this agent does"
                rows="3"
              />
            </div>

            <div class="space-y-2">
              <Label for="model">Language Model</Label>
              <Select v-model="formData.model_id">
                <SelectTrigger :disabled="loadingModels">
                  <SelectValue placeholder="Select a model" />
                </SelectTrigger>
                <SelectContent>
                  <div v-if="loadingModels" class="p-2 text-center text-sm text-muted-foreground">
                    Loading models...
                  </div>
                  <SelectItem
                    v-else
                    v-for="model in availableModels"
                    :key="model.id"
                    :value="model.id"
                  >
                    <div class="flex flex-col">
                      <span>{{ model.name }}</span>
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Step 2: Tools & Instructions -->
      <div v-if="currentStep === 1">
        <Card>
          <CardContent class="pt-6 space-y-4">
            <div class="space-y-2">
              <Label>Tool Categories</Label>
              <div v-if="loadingTools" class="text-sm text-muted-foreground p-4 text-center">
                Loading available tools...
              </div>
              <div v-else>
                <!-- Selected Tools -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <Card v-for="key in formData.tool_categories" :key="key" class="relative">
                    <Button
                      variant="ghost"
                      size="icon"
                      class="absolute right-2 top-2"
                      @click="formData.tool_categories = formData.tool_categories?.filter(t => t !== key)"
                    >
                      <X class="h-4 w-4" />
                    </Button>
                    <CardContent class="pt-6">
                      <h3 class="font-medium">{{ availableTools[key]?.name }}</h3>
                      <p class="text-sm text-muted-foreground mt-1">{{ availableTools[key]?.description }}</p>
                    </CardContent>
                  </Card>
                </div>

                <!-- Add Tool Button -->
                <Select v-model="selectedTool" class="w-full">
                  <SelectTrigger>
                    <SelectValue placeholder="Select a tool category to add" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem
                      v-for="(category, key) in availableTools"
                      :key="key"
                      :value="key"
                      :disabled="formData.tool_categories?.includes(key)"
                    >
                      <div class="flex flex-col">
                        <span>{{ category.name }}</span>
                        <span class="text-sm text-muted-foreground">{{ category.description }}</span>
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>

              </div>
            </div>

            <div class="space-y-2">
              <Label for="instructions">Custom Instructions</Label>
              <Textarea
                id="instructions"
                v-model="formData.custom_instructions"
                placeholder="Add any specific instructions for the agent"
                rows="4"
              />
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Step 3: Review -->
      <div v-if="currentStep === 2">
        <Card>
          <CardContent class="pt-6">
            <div class="space-y-4">
              <div>
                <h3 class="font-medium mb-1">Basic Information</h3>
                <p><span class="font-medium">Name:</span> {{ formData.name }}</p>
                <p><span class="font-medium">Model:</span> {{ formData.model_id }}</p>
                <p v-if="formData.description"><span class="font-medium">Description:</span> {{ formData.description }}</p>
              </div>

              <div v-if="formData.tool_categories?.length">
                <h3 class="font-medium mb-1">Selected Tools</h3>
                <div class="flex flex-wrap gap-1">
                  <Badge 
                    v-for="tool in formData.tool_categories" 
                    :key="tool"
                    variant="secondary"
                  >
                    {{ tool }}
                  </Badge>
                </div>
              </div>

              <div v-if="formData.custom_instructions">
                <h3 class="font-medium mb-1">Custom Instructions</h3>
                <p class="text-sm">{{ formData.custom_instructions }}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div class="flex justify-between mt-6">
        <Button
          v-if="currentStep > 0"
          variant="outline"
          @click="prevStep"
        >
          Previous
        </Button>
        <div class="ml-auto">
          <Button
            v-if="currentStep < 2"
            :disabled="!isStepValid"
            @click="nextStep"
          >
            Next
          </Button>
          <Button
            v-else
            :disabled="!isStepValid"
            @click="handleSubmit"
          >
            Create Agent
          </Button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>
