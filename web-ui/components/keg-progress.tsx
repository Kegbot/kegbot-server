import Box from "@mui/material/Box";
import LinearProgress from "@mui/material/LinearProgress";
import Typography from "@mui/material/Typography";
import type { Keg } from "@/api-client";
import { useFormatters } from "@/components/use-formatters";
import { kegPercentFull } from "@/lib/format";

/** Fill bar for a keg, with remaining-volume label. */
export function KegProgress({ keg }: { keg: Keg }) {
  const { volume } = useFormatters();
  const fullMl = keg.full_volume_ml ?? 0;
  const spilledMl = keg.spilled_ml ?? 0;
  const percent = kegPercentFull(keg.served_volume_ml, spilledMl, fullMl);
  const remaining = Math.max(0, fullMl - keg.served_volume_ml - spilledMl);
  const color = percent < 10 ? "error" : percent < 25 ? "warning" : "success";
  return (
    <Box>
      <LinearProgress
        variant="determinate"
        value={percent}
        color={color}
        sx={{ height: 10, borderRadius: 1 }}
      />
      <Typography variant="caption" color="text.secondary">
        {percent.toFixed(0)}% full ({volume(remaining)} remaining)
      </Typography>
    </Box>
  );
}
