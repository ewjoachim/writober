const WORKFLOW_URL =
  "https://api.github.com/repos/ewjoachim/writober/actions/workflows/publish.yml/dispatches";

export default {
  async scheduled(controller, env, ctx) {
    const parisHour = new Intl.DateTimeFormat("en-GB", {
      timeZone: "Europe/Paris",
      hour: "2-digit",
      hourCycle: "h23",
    }).format(new Date(controller.scheduledTime));
    if (parisHour !== "00") return; // the other cron line, wrong side of the DST offset

    const res = await fetch(WORKFLOW_URL, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${env.GITHUB_TOKEN}`,
        Accept: "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "writober-midnight", // GitHub rejects requests without one
      },
      body: JSON.stringify({ ref: "main" }),
    });
    if (res.status !== 204) {
      throw new Error(`dispatch failed: ${res.status} ${await res.text()}`);
    }
  },
};
