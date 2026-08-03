import Box from "@mui/material/Box";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import type { Keg } from "@/api-client";
import { useFormatters } from "@/components/use-formatters";
import { kegPercentFull } from "@/lib/format";
import { MONO_FONT } from "@/theme/typography";

/**
 * Keg fill gauge: amber fill on a ticked track, with a mono readout.
 * Low levels change the readout color, not the fill.
 */
export function KegProgress({ keg }: { keg: Keg }) {
  const { volume } = useFormatters();
  const fullMl = keg.full_volume_ml ?? 0;
  const spilledMl = keg.spilled_ml ?? 0;
  const percent = kegPercentFull(keg.served_volume_ml, spilledMl, fullMl);
  const remaining = Math.max(0, fullMl - keg.served_volume_ml - spilledMl);
  const readoutColor = percent < 10 ? "error.main" : percent < 25 ? "warning.main" : "text.primary";

  return (
    <Box>
      <Box
        sx={{
          position: "relative",
          height: 12,
          borderRadius: 6,
          bgcolor: "action.hover",
          border: 1,
          borderColor: "divider",
          overflow: "hidden",
        }}
      >
        <Box
          sx={{
            width: `${percent}%`,
            height: "100%",
            bgcolor: "primary.main",
            borderRadius: "inherit",
            transition: "width 300ms ease",
          }}
        />
        {[25, 50, 75].map((tick) => (
          <Box
            key={tick}
            sx={{
              position: "absolute",
              left: `${tick}%`,
              top: 0,
              bottom: 0,
              width: "1px",
              bgcolor: "background.paper",
              opacity: 0.7,
            }}
          />
        ))}
      </Box>
      <Stack direction="row" sx={{ justifyContent: "space-between", mt: 0.5 }}>
        <Typography
          variant="caption"
          sx={{ fontFamily: MONO_FONT, fontWeight: 600, color: readoutColor }}
        >
          {percent.toFixed(0)}% FULL
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {volume(remaining)} remaining
        </Typography>
      </Stack>
    </Box>
  );
}
