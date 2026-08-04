import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import type { ReactNode } from "react";
import { useFormatters } from "@/components/use-formatters";
import type { StatsBlob } from "@/lib/stats";
import { MONO_FONT } from "@/theme/typography";

export interface StatCell {
  value: ReactNode;
  caption: string;
}

function Cell({ value, caption, index }: StatCell & { index: number }) {
  return (
    <Box
      sx={{
        px: 2.5,
        py: 1.75,
        borderColor: "divider",
        borderLeft: { xs: index % 2 === 1 ? 1 : 0, sm: index > 0 ? 1 : 0 },
        borderTop: { xs: index >= 2 ? 1 : 0, sm: 0 },
        borderStyle: "solid",
        borderRight: 0,
        borderBottom: 0,
        minWidth: 0,
      }}
    >
      <Typography
        sx={{
          fontFamily: MONO_FONT,
          fontWeight: 600,
          fontSize: "1.5rem",
          lineHeight: 1.3,
          overflow: "hidden",
          textOverflow: "ellipsis",
          whiteSpace: "nowrap",
        }}
      >
        {value}
      </Typography>
      <Typography variant="overline" color="text.secondary" component="div">
        {caption}
      </Typography>
    </Box>
  );
}

/** Headline stat strip: one surface, hairline-divided cells. */
export function StatStrip({ cells }: { cells: StatCell[] }) {
  return (
    <Paper
      variant="outlined"
      sx={{
        display: "grid",
        gridTemplateColumns: { xs: "1fr 1fr", sm: `repeat(${cells.length}, 1fr)` },
        overflow: "hidden",
      }}
    >
      {cells.map((cell, index) => (
        <Cell key={cell.caption} {...cell} index={index} />
      ))}
    </Paper>
  );
}

/** Site-wide headline stats derived from a stats blob. */
export function StatBadges({ stats }: { stats: StatsBlob }) {
  const { volume } = useFormatters();
  return (
    <StatStrip
      cells={[
        { value: volume(stats.total_volume_ml ?? 0), caption: "total poured" },
        { value: stats.total_pours ?? 0, caption: "pours" },
        { value: stats.registered_drinkers?.length ?? 0, caption: "drinkers" },
        { value: stats.sessions_count ?? 0, caption: "sessions" },
      ]}
    />
  );
}
