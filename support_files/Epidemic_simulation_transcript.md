[00:00:00] - [Narrator] Hey, there.
[00:00:01] In this video, we're gonna simulate
[00:00:02] some different versions of an infectious disease
[00:00:04] to try to get a handle on the basics.
[00:00:06] We'll explore three phases.
[00:00:08] The epidemic phase, when the disease is new.
[00:00:10] The endemic phase,
[00:00:11] when the disease has been around for a while.
[00:00:14] And the eradication phase,
[00:00:15] when we finally get rid of the disease for good.
[00:00:20] This city has two kinds of locations: homes and non-homes.
[00:00:25] Three blobs live in each home and each day,
[00:00:27] each blob will go to up to three different places
[00:00:29] near where it lives
[00:00:30] and then return home at the end of the day.
[00:00:32] The disease will have three different states.
[00:00:35] Blobs start out blue in the susceptible state.
[00:00:37] If a blob catches the disease, it becomes infectious
[00:00:41] and can then infect other blobs that are in the same room.
[00:00:44] Blobs stay infectious for two days
[00:00:46] and then they enter this recovered state, turning gray.
[00:00:49] And in this model, recovered blobs are permanently immune.
[00:00:52] This is called an SIR model.
[00:00:54] This is, obviously, a lot simpler than real life,
[00:00:56] so we're not going to try to make
[00:00:58] any specific predictions about COVID-19,
[00:01:00] but the goal here is to get a feel
[00:01:01] for the overall patterns of disease spread,
[00:01:04] so this should do the trick.
[00:01:06] All right, let's run our first full simulation.
[00:01:09] We'll start with 10 infected blobs
[00:01:10] and an infection chance of 1%
[00:01:12] each time blobs interact in the same room.
[00:01:23] Let's pause here.
[00:01:24] This graph stacks numbers
[00:01:26] from the three different states on top of each other.
[00:01:28] For example, at the end of the third day,
[00:01:30] out of the 1,000 blobs,
[00:01:32] 798 of them are susceptible,
[00:01:34] 172 are infectious,
[00:01:35] and the other 30 have already recovered.
[00:01:38] This R-naught number that I mysteriously put up here
[00:01:41] is called the basic reproduction number.
[00:01:43] It's the number of new infections
[00:01:45] caused by each infectious blob before it recovers,
[00:01:48] on average assuming there's no immunity.
[00:01:50] For example, if R-naught equals three
[00:01:52] and we start with two infectious blobs,
[00:01:54] each would infect three more blobs on average
[00:01:57] and stop being infectious itself.
[00:01:59] So the new number of infectious blobs
[00:02:01] would multiply by three getting to six total.
[00:02:04] And this multiplication repeats
[00:02:06] leading to exponential growth.
[00:02:08] At least, that's what we would expect.
[00:02:10] The real world is chaos though,
[00:02:12] so it doesn't work out so cleanly.
[00:02:14] That's one reason I like running simulations.
[00:02:16] They force us to look at the messiness.
[00:02:18] Here, R-naught was calculated by averaging
[00:02:20] over many possible versions of the simulation
[00:02:22] all with the same settings.
[00:02:24] The result is 2.5 so if everything were clean and tidy,
[00:02:27] we'd see the number of infections multiply by 2.5
[00:02:31] over the two-day infectious period.
[00:02:32] But at least for this run, the growth is quite a bit faster.
[00:02:35] This is part of why we don't
[00:02:37] precisely know R-naught for COVID-19.
[00:02:39] In the real world,
[00:02:40] we don't get to run the simulation a bunch of times
[00:02:42] to average things out.
[00:02:44] Anyway, let's see what happens as we keep going.
[00:02:47] As more and more blobs become infected,
[00:02:49] the growth slows down.
[00:02:50] R-naught pretends that all the blobs are susceptible,
[00:02:52] but that quickly becomes untrue
[00:02:55] so we should really add this factor S here
[00:02:57] for the fraction of blobs that actually are susceptible.
[00:03:00] R-naught times S is given its own symbol,
[00:03:02] usually R but sometimes RT.
[00:03:05] It's like R-naught but for some later time
[00:03:06] when immunity is slowing things down.
[00:03:08] Instead of the basic reproduction number,
[00:03:10] R is just called the regular reproduction number.
[00:03:14] And as long as I'm throwing some terms at you,
[00:03:16] S goes down over time so instead of exponential growth,
[00:03:19] this becomes logistic growth
[00:03:20] which flattens out after a while.
[00:03:22] We won't dwell on logistic growth here,
[00:03:24] but I'll link to some videos in case you're interested
[00:03:26] in going more deeply into the math.
[00:03:28] When R is above one, the epidemic is still growing.
[00:03:31] When it's equal to one,
[00:03:32] the number of active cases stops growing.
[00:03:34] And when it's less than one, the cases decline.
[00:03:38] And when this fraction of susceptibles is small enough
[00:03:40] for R to go to one, it's called herd immunity,
[00:03:42] which we'll talk more about later.
[00:03:44] But one thing we should note now,
[00:03:46] herd immunity means the number of cases will start dropping,
[00:03:49] but it's not an absolute cap.
[00:03:51] The total number of cases can go much higher
[00:03:53] if a lot of cases are happening at the same time.
[00:03:56] In this case, at the peak of active cases,
[00:03:58] 41% were infectious at the same time.
[00:04:00] And when all was said and done,
[00:04:02] 85% were infected at one point or another.
[00:04:06] So that's the basic shape of an epidemic,
[00:04:08] but let's run through a few more simulations
[00:04:10] with different infection rates to get a better sense
[00:04:12] of what different situations might look like.
[00:04:15] I picked infection rates that would lead to
[00:04:17] R-naught values of 1.5, 1.1, and 0.9.
[00:04:20] (classical music)
[00:04:30] Looking at R-naught equals 2.5 again,
[00:04:32] the results are pretty close to what we saw last time.
[00:04:35] When R-naught equals 1.5, as we'd expect,
[00:04:38] we'd see a smaller peak and fewer cases overall,
[00:04:40] but it's still a pretty large portion of the population.
[00:04:44] When R-naught is 1.1,
[00:04:45] there's still an exponential light growth at the beginning,
[00:04:48] but it's just a 10% increase every two days
[00:04:51] so we don't see a big spike this time.
[00:04:54] And when R-naught equals 0.9,
[00:04:56] it's less than one so we expect the disease to decline
[00:04:59] even before any immunity builds up.
[00:05:01] And it's good to see that that is indeed what happens.
[00:05:05] Right now, you might be thinking as I was,
[00:05:07] okay, I get that R-naught determines whether it'll grow,
[00:05:10] but how do things like the length of the infectious period
[00:05:12] or the size of the population
[00:05:14] affect how the growth plays out?
[00:05:16] To help answer this,
[00:05:17] I made some more variations on that first sim.
[00:05:20] The first one has the same settings as before
[00:05:22] with a two-day infectious period and 1,000 blobs.
[00:05:25] The second has an infectious period of one day
[00:05:27] instead of two.
[00:05:29] The third one has an infectious period of 10 days.
[00:05:32] And the last one has 10,000 instead of 1,000 blobs.
[00:05:35] And in each case, I adjusted the infection chance
[00:05:37] to keep R-naught close to 2.5.
[00:05:40] Before we hit go, try making some predictions
[00:05:42] about the peak number of infections,
[00:05:44] the total number of infections,
[00:05:46] and anything else you think might or might not vary.
[00:05:49] (classical music)
[00:06:14] Not too surprisingly, the timelines are different.
[00:06:16] The one-day infection peaked and burned out quickly,
[00:06:19] the 10-day infection took longer,
[00:06:21] and in the city with 10,000 blobs,
[00:06:23] it also took longer for the disease to spread
[00:06:25] from 10 initial blobs to a significant portion
[00:06:27] of that larger population.
[00:06:29] But the peak and total infection percentages
[00:06:32] turned out to be almost the same in each case.
[00:06:35] The only thing slowing the spread
[00:06:36] in these simulations is herd immunity
[00:06:38] so the fraction infected stays pretty steady
[00:06:41] in different situations with the same R-naught.
[00:06:43] I chose 2.5 as the example R-naught
[00:06:45] because that's in the range
[00:06:46] of early estimates of R-naught for COVID-19.
[00:06:49] There's some uncertainty there
[00:06:50] and it'll be different in different places,
[00:06:52] but according to our current understanding of the disease,
[00:06:55] if we did nothing at all,
[00:06:56] it would be reasonable to expect something like this.
[00:06:59] So that's what's worrying about it.
[00:07:02] All right, that's the epidemic phase.
[00:07:04] On to the endemic phase.
[00:07:08] In our model so far,
[00:07:09] the disease ends up dying off all by itself.
[00:07:12] Unfortunately, this doesn't happen in real life though.
[00:07:15] There are two reasons for this.
[00:07:16] First, immunity is often not perfect or permanent.
[00:07:20] And second, long-term immunity isn't inherited
[00:07:23] so there's always a constant stream
[00:07:25] of new susceptible people.
[00:07:27] To put this into our model,
[00:07:28] we'll give the blobs an average lifespan of three weeks.
[00:07:31] At the beginning of a simulation,
[00:07:32] the ages will be all spread out
[00:07:34] and then when an older blob dies,
[00:07:36] it'll be replaced by a new susceptible blob.
[00:07:39] So with that in place, let's run some more sims.
[00:07:42] This time, we'll track R-naught and R in real time.
[00:07:45] R-naught is still gonna be calculated
[00:07:46] from an average of many sims,
[00:07:48] but R is gonna be based on counting the new infections
[00:07:51] on this one run of the simulation
[00:07:53] so it'll bounce around a bit based on random happenings
[00:07:55] especially when the numbers are small,
[00:07:57] but it will let us see the growth in real time.
[00:07:59] Anyway, here we go.
[00:08:01] (electronic music)
[00:08:16] Now we can see a little bit more clearly
[00:08:17] why infectious diseases don't go away on their own.
[00:08:20] At first, there is this initial epidemic
[00:08:22] with R greater than one just like before.
[00:08:25] And then, again, we get to a point where R is less than one
[00:08:28] leading to a decline.
[00:08:30] But this time, the infection count doesn't decline
[00:08:32] all the way to zero.
[00:08:34] Once it gets low, the number of susceptible blobs
[00:08:36] starts increasing again and in turn, R climbs back above one
[00:08:40] and then the number of infections starts to rise again.
[00:08:42] There's an equilibrium here
[00:08:44] with R always getting pulled back toward one.
[00:08:46] And as we saw before, on average,
[00:08:48] we expect R to be one at the herd immunity level.
[00:08:53] We can calculate the herd immunity level
[00:08:55] for any value of R-naught.
[00:08:56] As we said before, R-naught times S equals R
[00:09:00] and herd immunity is where R equals one
[00:09:02] so the fraction of susceptibles
[00:09:04] for herd immunity is one over R-naught.
[00:09:07] And herd immunity is usually given
[00:09:09] in terms of the fraction of people no longer susceptible
[00:09:12] so it ends up being one minus one over R-naught.
[00:09:16] When R-naught equals 2.5, we get 60%.
[00:09:19] If you've heard estimates
[00:09:20] of 50-70% for herd immunity for COVID-19,
[00:09:24] this is where that range comes from.
[00:09:26] Before we move on to the eradication phase,
[00:09:28] I wanna say again that the goal here is to get a sense
[00:09:31] for the broad patterns at play.
[00:09:33] The size and the timings of these cycles
[00:09:35] and the average number of people infected will depend a lot
[00:09:37] on the properties of the real disease
[00:09:39] and how we react to it.
[00:09:41] And there are some other factors like seasonality
[00:09:43] or mutations that can complicate this picture.
[00:09:45] But even with these real world complications in place,
[00:09:48] an endemic disease always fluctuates
[00:09:50] around this herd immunity equilibrium.
[00:09:54] All right, on to eradication.
[00:09:59] 10 days into the simulations,
[00:10:01] the blob city will discover a vaccine.
[00:10:03] After that point, when a blob dies and a new blob appears,
[00:10:06] that blob will have a chance
[00:10:07] of getting vaccinated, turning green.
[00:10:10] They're just like the gray recovered blobs
[00:10:12] but they're green instead so we can keep track of them.
[00:10:15] We'll again use this disease with R-naught equals 2.5.
[00:10:18] Here, herd immunity is when 40% are susceptible
[00:10:21] or when 60% are not susceptible
[00:10:24] so I would expect a 60% vaccination rate
[00:10:26] to get rid of the disease, but we should check that
[00:10:29] and let's also look at 50%, 35%, and 20%.
[00:10:33] Again, before we hit go, try to make some predictions.
[00:10:36] Will 60% actually result in eradication
[00:10:39] and what will happen with the lower rates?
[00:10:43] (electronic music)
[00:11:08] All right, so 60% did indeed do the job,
[00:11:10] but none of the others did.
[00:11:12] Before running these,
[00:11:13] I'll admit that I thought that 50% might do it
[00:11:16] since some blobs would be immune
[00:11:17] from actually having the disease,
[00:11:19] but it turns out that as long as there is room
[00:11:21] between this vaccination floor
[00:11:22] and the herd immunity threshold,
[00:11:24] the disease still has room to wobble around in equilibrium.
[00:11:28] True eradication turns out to be really hard.
[00:11:31] We'd have to do this for all populations
[00:11:33] that can carry the disease.
[00:11:34] This is hard enough for humans,
[00:11:36] but for many diseases, it includes animals too.
[00:11:39] So that's just infeasible.
[00:11:42] But eradication isn't the only goal.
[00:11:44] More vaccinations still mean smaller spikes in infections
[00:11:46] and fewer sick blobs overall.
[00:11:50] It's encouraging to think about being able to manage,
[00:11:53] if not eradicate a disease,
[00:11:54] but right now we're still very much in the epidemic phase.
[00:11:57] If you find yourself doing okay right now
[00:11:59] and want to find some way to help
[00:12:01] but just aren't sure what to do,
[00:12:03] one thing you can do is hit that button below the video
[00:12:05] to donate any amount to GiveDirectly.
[00:12:09] GiveDirectly puts your donations
[00:12:10] directly in the hands of other humans in need.
[00:12:13] It's a top rated charity
[00:12:14] for making donation dollars do the most good.
[00:12:16] It's tax deductible and the button is right there.
[00:12:20] Whether you're in a place to give or not,
[00:12:21] I do appreciate you watching to the end.
[00:12:24] Thanks.
[00:12:30] (soft classical music)