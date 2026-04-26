export function ChartSkeleton({ height = 300 }: { height?: number }) {
  return (
    <div className="bg-peec-tint rounded-peec-xl animate-pulse" style={{ height }} />
  );
}
