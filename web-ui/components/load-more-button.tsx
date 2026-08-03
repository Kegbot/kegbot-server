import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import CircularProgress from "@mui/material/CircularProgress";
import type { CursorList } from "@/lib/use-cursor-list";

/** "Load more" footer for cursor-paginated lists. */
export function LoadMoreButton({ list }: { list: CursorList<unknown> }) {
  if (!list.hasMore) {
    return null;
  }
  return (
    <Box sx={{ display: "flex", justifyContent: "center", py: 1 }}>
      <Button onClick={list.loadMore} disabled={list.loadingMore} variant="outlined">
        {list.loadingMore ? <CircularProgress size={20} /> : "Load more"}
      </Button>
    </Box>
  );
}
