import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardMedia from "@mui/material/CardMedia";
import MuiLink from "@mui/material/Link";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import { Link, useParams } from "react-router";
import { drinksList, drinksPictureDestroy, drinksRetrieve } from "@/api-client";
import { useConfirm } from "@/components/confirm-context";
import { useCurrentUser } from "@/components/current-user-context";
import { DrinkList } from "@/components/drink-list";
import { Page } from "@/components/page";
import { Section } from "@/components/section";
import { useSnackbar } from "@/components/snackbar-context";
import { StatStrip } from "@/components/stat-badges";
import { useFormatters } from "@/components/use-formatters";
import { UserLink } from "@/components/user-link";
import { toErrorMessage, unwrap } from "@/lib/api";
import { formatDateTime, formatDuration } from "@/lib/format";
import { useAsyncData } from "@/lib/use-async-data";

export function DrinkView() {
  const params = useParams();
  const drinkId = Number(params.id);
  const { volume } = useFormatters();
  const { user } = useCurrentUser();
  const confirm = useConfirm();
  const { showMessage } = useSnackbar();

  const drink = useAsyncData(() => unwrap(drinksRetrieve({ path: { id: drinkId } })), {
    deps: [drinkId],
  });

  const sessionId = drink.data?.session_id ?? null;
  const sessionDrinks = useAsyncData(
    async () => {
      if (sessionId == null) {
        return [];
      }
      const page = await unwrap(drinksList({ query: { session: sessionId, page_size: 11 } }));
      return (page.results ?? []).filter((other) => other.id !== drinkId).slice(0, 10);
    },
    { deps: [sessionId, drinkId], enabled: sessionId != null },
  );

  const canManagePicture = user !== null && (user.is_staff || user.id === drink.data?.user?.id);

  const deletePicture = async () => {
    if (
      !(await confirm({
        title: "Erase this picture?",
        message: "The image will be permanently deleted.",
        confirmText: "Erase",
        destructive: true,
      }))
    ) {
      return;
    }
    try {
      await unwrap(drinksPictureDestroy({ path: { id: drinkId } }));
      showMessage("Picture erased.");
      drink.reload();
    } catch (error) {
      showMessage(toErrorMessage(error), "error");
    }
  };

  return (
    <Page
      title={
        drink.data
          ? `${volume(drink.data.volume_ml)} of ${drink.data.keg.beverage.name}`
          : `Drink #${drinkId}`
      }
      eyebrow={`Drink #${drinkId}`}
      meta={
        drink.data && (
          <>
            poured by <UserLink user={drink.data.user} avatarSize={0} /> ·{" "}
            {formatDateTime(drink.data.time)}
          </>
        )
      }
      width="content"
      loading={drink.loading}
      error={drink.error}
    >
      {drink.data && (
        <Stack spacing={4}>
          {drink.data.shout && (
            <Typography
              variant="h5"
              component="blockquote"
              sx={{
                fontStyle: "italic",
                fontWeight: 500,
                borderLeft: 2,
                borderColor: "primary.main",
                pl: 2,
              }}
            >
              “{drink.data.shout}”
            </Typography>
          )}
          <StatStrip
            cells={[
              { value: volume(drink.data.volume_ml), caption: "volume" },
              { value: formatDuration(drink.data.duration), caption: "pour time" },
              {
                value:
                  sessionId != null ? (
                    <MuiLink
                      component={Link}
                      to={`/sessions/id/${sessionId}`}
                      underline="hover"
                      color="inherit"
                    >
                      #{sessionId}
                    </MuiLink>
                  ) : (
                    "—"
                  ),
                caption: "session",
              },
              {
                value: (
                  <MuiLink
                    component={Link}
                    to={`/kegs/${drink.data.keg.id}`}
                    underline="hover"
                    color="inherit"
                  >
                    #{drink.data.keg.id}
                  </MuiLink>
                ),
                caption: `keg · ${drink.data.keg.beverage.name}`,
              },
            ]}
          />
          {drink.data.picture?.resized_url && (
            <Section label="Photo">
              <Card variant="outlined" sx={{ maxWidth: 480 }}>
                <CardMedia
                  component="img"
                  image={drink.data.picture.resized_url}
                  alt="Drink picture"
                />
                {canManagePicture && (
                  <Button color="error" onClick={() => void deletePicture()} sx={{ m: 1 }}>
                    Erase picture
                  </Button>
                )}
              </Card>
            </Section>
          )}
          {(sessionDrinks.data?.length ?? 0) > 0 && (
            <Section
              label="More from this session"
              action={
                sessionId != null && (
                  <MuiLink
                    component={Link}
                    to={`/sessions/id/${sessionId}`}
                    underline="hover"
                    variant="body2"
                  >
                    View session
                  </MuiLink>
                )
              }
            >
              <DrinkList drinks={sessionDrinks.data ?? []} hideKeg />
            </Section>
          )}
        </Stack>
      )}
    </Page>
  );
}
