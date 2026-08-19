// TUTUNAKU — SkeletonPage loader global
export default function SkeletonPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center
                    bg-[var(--color-bg)] gap-6 animate-pulse">
      {/* Logo pulse */}
      <div className="w-24 h-24 rounded-full bg-gradient-to-br from-alebrije-coral/30
                      to-alebrije-teal/30" />
      <div className="space-y-3 w-64">
        <div className="h-4 bg-gray-200 dark:bg-dark-muted rounded-full" />
        <div className="h-4 bg-gray-200 dark:bg-dark-muted rounded-full w-3/4 mx-auto" />
      </div>
      <p className="text-[var(--color-muted)] text-sm font-semibold animate-pulse">
        Cargando Tutunaku...
      </p>
    </div>
  )
}
