import Button from "@mui/material/Button";
import MuiLink from "@mui/material/Link";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import Stack from "@mui/material/Stack";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import { useState } from "react";
import { Link } from "react-router";
import type { Drink } from "@/api-client";
import { drinksDestroy, drinksList, drinksReassignCreate } from "@/api-client";
import { useConfirm } from "@/components/confirm-context";
import { LoadMoreButton } from "@/components/load-more-button";
import { Page } from "@/components/page";
import { usePrompt } from "@/components/prompt-context";
import { useSnackbar } from "@/components/snackbar-context";
import { useFormatters } from "@/components/use-formatters";
import { UserLink } from "@/components/user-link";
import { toErrorMessage, unwrap } from "@/lib/api";
import { formatDateTime } from "@/lib/format";
import { useCursorList } from "@/lib/use-cursor-list";
import { MONO_FONT } from "@/theme/typography";

function DrinkActions({ drink, onChanged }: { drink: Drink; onChanged: () => void }) {
  const confirm = useConfirm();
  const prompt = usePrompt();
  const { showMessage } = useSnackbar();
  const [anchor, setAnchor] = useState<HTMLElement | null>(null);

  const cancel = async (spilled: boolean) => {
    setAnchor(null);
    if (
      !(await confirm({
        title: spilled ? "Cancel drink and record as spill?" : "Cancel this drink?",
        message: "The drink will be permanently deleted and stats recomputed.",
        confirmText: "Cancel drink",
        destructive: true,
      }))
    ) {
      return;
    }
    try {
      await unwrap(
        drinksDestroy({
          path: { id: drink.id },
          query: { spilled: spilled || undefined } as never,
        }),
      );
      showMessage("Drink canceled.");
      onChanged();
    } catch (error) {
      showMessage(toErrorMessage(error), "error");
    }
  };

  const reassign = async () => {
    setAnchor(null);
    const username = await prompt({
      title: `Reassign drink #${drink.id}`,
      label: "Username",
      confirmText: "Reassign",
    });
    if (!username) {
      return;
    }
    try {
      await unwrap(drinksReassignCreate({ path: { id: drink.id }, body: { username } }));
      showMessage(`Drink reassigned to ${username}.`);
      onChanged();
    } catch (error) {
      showMessage(toErrorMessage(error), "error");
    }
  };

  return (
    <>
      <Button size="small" onClick={(e) => setAnchor(e.currentTarget)}>
        Actions
      </Button>
      <Menu anchorEl={anchor} open={anchor !== null} onClose={() => setAnchor(null)}>
        <MenuItem onClick={() => void reassign()}>Reassign…</MenuItem>
        <MenuItem onClick={() => void cancel(false)}>Cancel drink…</MenuItem>
        <MenuItem onClick={() => void cancel(true)}>Cancel as spill…</MenuItem>
      </Menu>
    </>
  );
}

export function DrinksAdminView() {
  const { volume } = useFormatters();
  const drinks = useCursorList((cursor) => unwrap(drinksList({ query: { cursor } })));

  return (
    <Page title="Drinks" loading={drinks.loading} error={drinks.error}>
      <Stack spacing={2}>
        <TableContainer sx={{ overflowX: "auto" }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Drink</TableCell>
                <TableCell>Time</TableCell>
                <TableCell>Drinker</TableCell>
                <TableCell align="right">Volume</TableCell>
                <TableCell>Keg</TableCell>
                <TableCell />
              </TableRow>
            </TableHead>
            <TableBody>
              {drinks.items.map((drink) => (
                <TableRow key={drink.id} hover>
                  <TableCell>
                    <MuiLink component={Link} to={`/drinks/${drink.id}`} underline="hover">
                      #{drink.id}
                    </MuiLink>
                  </TableCell>
                  <TableCell sx={{ color: "text.secondary", whiteSpace: "nowrap" }}>
                    {formatDateTime(drink.time)}
                  </TableCell>
                  <TableCell>
                    <UserLink user={drink.user} muted />
                  </TableCell>
                  <TableCell align="right" sx={{ fontFamily: MONO_FONT, whiteSpace: "nowrap" }}>
                    {volume(drink.volume_ml)}
                  </TableCell>
                  <TableCell>{drink.keg.beverage.name}</TableCell>
                  <TableCell align="right">
                    <DrinkActions drink={drink} onChanged={drinks.reload} />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <LoadMoreButton list={drinks} />
      </Stack>
    </Page>
  );
}
