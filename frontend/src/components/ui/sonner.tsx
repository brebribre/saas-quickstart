import { useTheme } from "@/contexts/ThemeContext"
import { Toaster as Sonner } from "sonner"

type ToasterProps = React.ComponentProps<typeof Sonner>

const Toaster = ({ ...props }: ToasterProps) => {
  const { theme } = useTheme()

  return (
    <Sonner
      theme={theme}
      className="toaster group"
      toastOptions={{
        classNames: {
          toast: "group toast bg-[hsl(var(--background))] border-[hsl(var(--border))] shadow-lg text-[hsl(var(--foreground))] rounded-md",
          description: "text-[hsl(var(--muted-foreground))]",
          actionButton: "bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]",
          cancelButton: "bg-[hsl(var(--muted))] text-[hsl(var(--muted-foreground))]",
        },
      }}
      {...props}
    />
  )
}

export { Toaster }
