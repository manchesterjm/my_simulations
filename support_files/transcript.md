[00:00:00] - Some things are not normal. By that I mean if you go out in the world and start measuring things like human height, IQ
[00:00:08] or the size of apples on a tree, you will find that for each of these things, most of the data clusters
[00:00:14] around some average value. This is so common that we call it the normal distribution,
[00:00:20] but some things in life are not like this - Nature shows power laws all over the place.
[00:00:27] That seems weird, like is nature tuning itself to criticality? - If you make a crude measure of how big is the world war by
[00:00:33] how many people it kills, you find that it follows a power law. The outcome will vary in size over
[00:00:40] 10 million, a hundred million. - It's a much more likelihood of really big events than you would expect from
[00:00:46] a normal distribution, and they will totally skew the average. - The system you're looking at doesn't have any
[00:00:52] inherent physical scale. It's really hard to know what's gonna happen next. - The more you measure, the bigger the average
[00:00:58] is, which is really weird. It sounds impossible. - It's, it's very important to try to understand, you know,
[00:01:04] which game you're playing and what are the payoffs going to be in the, in the long run.
[00:01:10] - In the late 1800s, Italian engineer Vilfredo Pareto, stumbled upon something no one had seen before.
[00:01:17] See, he suspected there might be a hidden pattern in how much money people make. So he gathered income tax records from Italy, England,
[00:01:24] France, and other European countries, and for each country he plotted the distribution of income.
[00:01:31] Each country he looked at, he saw the same pattern, a pattern which still holds in most countries to this day,
[00:01:38] and it's not a normal distribution. If you think about a normal distribution like height,
[00:01:43] there's a clearly defined average and extreme outliers basically never happen.
[00:01:48] I mean, you are never going to find someone who is say five times the average height. That would be physically impossible,
[00:01:55] but Pareto's income distributions were different. Take this curve for England, it shows the number of people
[00:02:00] who earn more than a certain income. The curve starts off declining steeply, most people earn relatively little,
[00:02:07] but then it falls away gradually much more slowly than a normal distribution would,
[00:02:12] and it spans several orders of magnitude. There were people who earned five times, 10 times,
[00:02:18] even a hundred times more than others. That kind of spread just wouldn't happen if income were
[00:02:23] normally distributed. Now to shrink this huge spread of data, Pareto calculated the logarithms of all the values
[00:02:30] and plotted those instead. In other words, he used a log log plot, and when he did that, the broad curve transformed
[00:02:38] into a straight line. The gradient was around negative 1.5. That means each time you double the income,
[00:02:45] say from 200 pounds to 400 pounds, the number of people earning at least that amount drops off by a factor
[00:02:51] of two to the power of 1.5, which is around 2.8. And this pattern holds for every doubling of income.
[00:02:58] So Pareto could describe the distribution of incomes with one simple equation. The number of people who earn an income greater than
[00:03:05] or equal to x is proportional to one over x to the power of 1.5.
[00:03:10] Now, that's what Pareto saw for England. But he performed the same analysis on data from Italy,
[00:03:16] France, Prussia, and a bunch of other countries, and he saw the same thing again and again.
[00:03:22] Each time the data transformed into a straight line and the gradients were remarkably similar.
[00:03:28] That meant Pareto could describe the income distribution in each country with the same equation, one over the income
[00:03:35] to some power where that power is just the absolute gradient of the logarithmic graph.
[00:03:42] This type of relationship is called a power law. When you move from the world of normal distributions
[00:03:48] to the world of power laws, things change dramatically. So to illustrate this, let's take a trip to the casino
[00:03:54] to play three different games. At table number one, you get 100 tosses of a coin.
[00:04:01] Each time you flip and it lands on heads, you win $1. So the question is, how much would you be prepared
[00:04:07] to pay to play this game? Well, we need to work out how much you'd expect to win in this game
[00:04:12] and then pay less than that expected value. So the probability of throwing ahead is one half, multiply
[00:04:19] that by $1 and multiply that by a hundred tosses. That gives you an expected payout of $50.
[00:04:25] So you should be willing to pay anything less than $50 to play this game. Sure, you might not win every time,
[00:04:31] but if you play the game hundreds of times, the small variations either side of the average will cancel out
[00:04:36] and you can expect to turn a profit. One of the first people to study this kind of problem was Abraham de Moivre in the early 1700s.
[00:04:44] He showed that if you plot the probability of each outcome, you get a bell-shaped curve, which was later coined the normal distribution,
[00:04:51] - Normal distributions. The traditional explanation is that when there are a lot of effects that are random that are adding up,
[00:04:58] that's when you expect normals. So like how tall I am depends on a lot of random things about my nutrition, about my parents',
[00:05:05] genetics, all kinds of things. But, but if they, if these random effects are additive, that
[00:05:11] is what tends to lead to normals. - At table number two, there's a slightly different game.
[00:05:17] You still get 100 tosses of the coin, but this time, instead of potentially winning a dollar on each flip,
[00:05:23] your winnings are multiplied by some factor. So you start out with $1
[00:05:29] and then every time you toss a head, you multiply your winnings by 1.1. If instead the coin lands on tails,
[00:05:36] you multiply your winnings by 0.9 and after a hundred tosses, you take home the total that is the dollar.
[00:05:42] You started with times the string of 1.1s and 0.9s. So how much should you pay to play this game?
[00:05:49] Well, on each flip, your payout can either grow or shrink and each is equally likely each time you toss the coin.
[00:05:57] So the expected factor, each turn is just 1.1 plus 0.9 divided by two, which is one.
[00:06:03] So if you start out with $1, then your expected payout is just $1. That means you should be willing
[00:06:09] to pay anything less than a dollar to play this game. Right? Well, if you look at the distribution of payouts,
[00:06:15] you can see that you could win big. If you tossed a hundred heads, you'd win 1.1 to the power of a hundred.
[00:06:21] That's almost $14,000, although the chance of that happening is around 1 in 10
[00:06:27] to the power of 30, you'd be more likely to win the lottery three times in a row. On the other hand, the median payout is around 61 cents.
[00:06:34] So if you're only playing the game one time and you want even odds of turning a profit,
[00:06:39] well then you should pay less than 61 cents. Though either way, if you played the game hundreds of times,
[00:06:45] your payout would average out to $1. Now watch what happens if we switch the x axis from a linear
[00:06:51] scale to a logarithmic scale. Well then you see the curve transforms into a normal distribution.
[00:06:56] That's why this type of distribution is called a log normal distribution. - When random effects multiply, if I have a certain wealth
[00:07:05] and then my wealth goes up by a certain percentage next year because of my investments, and then the year
[00:07:10] after that it, it changes by another random factor as opposed to adding, I'm multiplying year after year.
[00:07:17] If you have a big product of random numbers, when you take the log of a product, that's the sum of the logs.
[00:07:23] So if so, what was a product of random numbers then gets translated into sums of logs
[00:07:30] of random numbers, and that's what leads to this so-called log normal distribution and log normal distributions produce big inequalities.
[00:07:38] You don't just see a mean, you see a mean with a big long tail. It's much more likelihood of really big events in this case,
[00:07:46] tremendous wealth being obtained than you would expect from a normal distribution. - The reason this curve is so asymmetric is
[00:07:53] because the downside is capped at zero. So at most you could lose $1, but the upside can keep growing up to nearly $14,000.
[00:08:03] Now let's go on to table three. Again, you'll be tossing a coin, but this time you start out with a dollar
[00:08:09] and the payout doubles each time you toss the coin and you keep tossing until you get a heads.
[00:08:15] Then the game ends. So if you get heads on your first toss, you get $2. If you get a tails first
[00:08:22] and then get a heads on your second toss, you get $4. If you flipped two tails and then a head on your third toss, you'd get $8 and so on.
[00:08:30] If it took you to the Nth toss to get a heads, you would get 2 to the N dollars.
[00:08:35] So how much should you pay to play this game? Well, as in our previous example, we need
[00:08:40] to work out the expected value. So suppose you throw a head on your first try, the payout is $2
[00:08:46] and the probability of that outcome is a half. So the expected value of that toss is a dollar.
[00:08:52] If it takes you two tosses to get a heads, then the payout is $4 and the probability of that happening is one over four.
[00:08:59] So again, the expected value is $1. We also need to add in the chance that you flip heads on your third try.
[00:09:05] In that case, the payout is $8 and the probability of that happening is one over eight. So again, the expected value is $1,
[00:09:13] and we have to keep repeating this calculation over all possible outcomes. We have to keep adding $1 for each of the different options
[00:09:20] for flipping the coin, say 10 times until it lands on heads or a hundred times before you get heads.
[00:09:26] I know it's extremely unlikely, but the payout is so huge that the expected value of that outcome is still a dollar.
[00:09:33] So it still increases the expected value of the whole game. This means that theoretically, the total expected value
[00:09:40] of this game is infinite. This is known as the St. Petersburg paradox.
[00:09:47] If you look at the distribution of payouts, you can see it's uncapped. It spans across all orders of magnitude.
[00:09:53] You could get a payout of a thousand dollars, a hundred thousand dollars, or even a million dollars or more.
[00:09:59] And while a million dollar payout is unlikely, it's not that unlikely. It's around one in a million.
[00:10:06] Now, if you transform both axes to a log scale, you see a straight line with a gradient of negative one.
[00:10:12] The payout of the St. Petersburg paradox follows a power law. The specific power law in this case is that the probability
[00:10:18] of a payout x is equal to x to the power of negative one or 1 over x. In the previous games, when you have a normal distribution
[00:10:26] or even a log normal distribution, you can measure the width of that distribution. It's standard deviation,
[00:10:32] and in a normal distribution, 95% of the data fall within two standard deviations from the mean.
[00:10:38] But with a power law, like in the St. Petersburg paradox, there is no measurable width.
[00:10:43] The standard deviation is infinite. This makes power laws a fundamentally different beast
[00:10:50] with some very weird properties. - Imagine you take a bunch of random samples and then average them and then take more random
[00:10:57] samples and average them. You'll find that the average keeps going up, it doesn't converge,
[00:11:03] and the more you measure, the bigger the average is, which is really weird. It sounds impossible, but it's
[00:11:09] because it has such a heavy tail, meaning the probability of really whopping big events is so significant
[00:11:17] that if you keep measuring occasionally, you're gonna measure one of those extreme outliers and they will totally skew the average.
[00:11:24] It's sort of like saying, you know, if you're standing in a room with Bill Gates or Elon Musk, the average wealth in that room
[00:11:32] you know is gonna be a hundred billion dollars or something because the average is dominated by one outlier.
[00:11:39] - And that same idea, one outlier can dominate the average shows up online too.
[00:11:45] A handful of companies, servers and data centers hold the personal information of millions of people.
[00:11:50] So when one of them gets hacked, it can have ripple across the whole network.
[00:11:56] We've had scammers get a hold of email addresses and phone numbers of writers on our team and then send them messages pretending to be me.
[00:12:04] That is where today's sponsor, NordVPN comes in NordVPN encrypts your internet traffic,
[00:12:09] so your personal data stays private even when the wider system isn't. It protects you from hackers, trackers,
[00:12:15] and malware with threat protection, even when you're not connected to a VPN. Within just 15 minutes of registering a new email, we saw
[00:12:23] that five leaks had already been detected. NordVPN lets you browse securely from anywhere in the world
[00:12:28] by routing your connection through encrypted servers in over 60 countries. You can try it completely risk free
[00:12:34] with a 30 day money back guarantee. Just scan this QR code or go to nordvpn.com/veritasium
[00:12:41] to get a huge discount on a two year plan plus four extra months free. That's nordvpn.com/veritasium for a huge discount.
[00:12:49] I'll put the link down in the description. I'd like to thank NordVPN for sponsoring this video. And now back to power laws.
[00:12:56] So why do you get a power law from the simple St. Petersburg setup?
[00:13:01] If you look at the payout x, you can see it grows exponentially with each toss of the coin.
[00:13:07] x equals two to the N. But if you look at the probability of tossing the coin that many times to get a heads, you can see
[00:13:14] that this probability shrinks exponentially. So the probability of flipping a coin n times is a half
[00:13:20] to the power of n, but we're not really interested in the number of tosses. We're interested in the payout.
[00:13:26] Now we know that x equals two to the n. So instead of writing two to the n in our probability equation, we can just write x.
[00:13:32] So we end up with this. The probability of a payout of x dollars is equal to one over x,
[00:13:38] or in other words, x to the power of negative one. - You put them together, the exponentials
[00:13:45] conspire to make a power law. And that's a very common thing in nature, that a lot of times when we see power laws,
[00:13:51] there are two underlying exponentials that are dancing together to make a power law.
[00:13:57] - One example of this is earthquakes. If you look at data on earthquakes, you find that small earthquakes are very common,
[00:14:04] but earthquakes of increasing magnitudes become exponentially rarer.
[00:14:09] But the destruction that earthquakes cause is not proportional to their magnitude. It's proportional to the energy they release.
[00:14:15] And as earthquakes grow in magnitude, that energy grows exponentially. - So there's this exponential decay in frequency
[00:14:22] of earthquakes of a given magnitude and an exponential increase in the amount of energy released
[00:14:29] by earthquakes of a certain magnitude. So when you combine those two exponentials
[00:14:34] to eliminate the magnitude, what you find is a power law. - But power laws also reveal something deeper about the
[00:14:41] underlying structure of a system to see this in action. Let's go back to the third coin game in the
[00:14:46] St. Petersburg paradox. Now you can draw all the different outcomes as a tree diagram
[00:14:51] where the length of each branch is equal to its probability. So starting with a single line of length one
[00:14:56] and then a half for the first two branches, a quarter for the next four and so on. Now when you zoom in,
[00:15:03] you keep seeing the same structure repeating at smaller and smaller scales. It's self-similar like a fractal, and that's no coincidence.
[00:15:11] We see the same fractal-like pattern in the veins on a leaf river networks, the blood vessels in our
[00:15:17] lungs, even lightning. And in all of these cases, we can describe the pattern with a power law.
[00:15:23] Power laws and fractals are intrinsically linked. That's because power laws reveal something fundamental about
[00:15:30] a system structure. - So I've got a magnet and I've got a screw, and you'll notice if I bring them close together,
[00:15:36] then the screw gets attracted to the magnet, and that's because there's a lot of iron in it, which is ferromagnetic.
[00:15:42] But watch what happens if I start heating this up. Trying to, oh, you see that?
[00:15:48] Ah, there it went. There it went. You see, you heat it up and suddenly it becomes non-magnetic.
[00:15:54] To find out what happened, let's zoom in on this magnet. - Inside a magnet, each atom has its own magnetic moment,
[00:16:01] which means you can think of it like its own little magnet or compass. If one atom's moment points up, its neighbors tend
[00:16:07] to point that way too. Since this lowers the system's overall potential energy. Therefore at low temperatures,
[00:16:12] you get large regions called domains where all the moments align. And when many of these domains also align,
[00:16:19] their individual magnetic fields reinforce to create an overall field around the magnet.
[00:16:24] But if you heat up the magnet, each atom starts vibrating vigorously. The moments flip up and down,
[00:16:31] and so the alignment can break down. And when all the moments cancel out, then there's no longer a net magnetic field.
[00:16:38] Now, if you have the right equipment, you can balance any magnetic material right on that transition point, right between magnetic
[00:16:45] and non-magnetic. This is called the critical point, and it occurs at a specific temperature called
[00:16:51] the curie temperature. I asked Casper and the team to build a simulation to show what's going on
[00:16:57] inside the magnet at this critical point, - Each pixel represents the magnetic moment
[00:17:02] of an individual atom. Let's say red is up and blue is down. Now when the temperature is low, we get these big domains
[00:17:10] where the magnetic moments are all aligned and you get an overall magnetic field. But if we really crank up the temperature, then all
[00:17:18] of these moments start flipping up and down and so they cancel out and the magnet loses its magnetism.
[00:17:23] So that's exactly what happened in our demo. But if we tune the temperature just right, right to
[00:17:29] that Curie temperature, then the pattern becomes way more interesting. - This looks like a map, - Like a map?
[00:17:38] - Yeah, it almost looks like the Mediterranean or something. It's almost stable, like atoms
[00:17:44] that are pointing one way tend to point that way for a while, but there is clearly fluctuations as well.
[00:17:53] So domains are constantly coming and going. It's both got some elements of stability
[00:18:00] and some persistence over time. Some features which are consistent, but it's also not locked in place, right?
[00:18:08] Because you notice changes over time. - If you zoom in, you find that the same kinds
[00:18:14] of patterns repeat at all scales. You've got domains of tens of atoms, hundreds, thousands, even millions.
[00:18:20] There's just no inherent scale to the system that is, it's scale free. It's just like a fractal.
[00:18:26] And if you plot the size distribution of the domains, you get a power law.
[00:18:31] - The underlying geometry suddenly shows a fractal character that it doesn't have on either side of the phase transition.
[00:18:38] Right at the phase transition, you get fractal behavior and that pops out as a power law.
[00:18:43] - In fact, whenever you find a power law that indicates you're dealing with a system that has no intrinsic scale
[00:18:49] and that is a signature of a system in a critical state, which turns out has huge consequences.
[00:18:56] - See normally in a magnet below the Curie temperature, each atom influences only its neighbors. If one atom's magnetic moment flips up, then that means
[00:19:04] that its neighbors are slightly more likely to point up too. But that influence is local, it dies out just a few atoms away.
[00:19:11] But as the magnet approaches its critical temperature, those local influences start to chain together.
[00:19:16] One spin notches its neighbor and that neighbor notches the next and so on, like a rumor spreading through a crowd.
[00:19:22] And the result is that the effective range of influence keeps expending. And right at the critical point,
[00:19:28] it becomes effectively infinite. A flip on one side can cascade throughout the
[00:19:33] entire material. So you get these small causes, just a single flip
[00:19:38] to reverberate throughout the entire system. - And it gets right into that, that point where
[00:19:45] the system is maximally unstable, anything can happen. It's also maximally interesting,
[00:19:50] in a way it's, it means the system is most unpredictable, most uncertain.
[00:19:56] It's really hard to know what's gonna happen next. And that seems to be a a, a natural procedure that happens in many different systems in the world.
[00:20:03] - One such system is forest fires. In June, 1988,
[00:20:08] a lightning strike started a small fire near Yellowstone National Park. This was nothing outta the ordinary.
[00:20:14] Each year, Yellowstone experiences thousands of lightning strikes. Most don't cause fires, and those that do tend to burn a few trees,
[00:20:21] maybe even a few acres before they fizzle out. Three quarters of fires burn less than a quarter of an acre.
[00:20:28] The largest fire in the park's recent history occurred in 1931. That burned through 18,000 acres,
[00:20:34] an area slightly larger than Manhattan. But the 1988 fire was different.
[00:20:39] That initial spark spread slowly at first covering several thousand acres. Then over the next couple of months, it merged
[00:20:46] with other small fires to create an enormous complex of mega fires that blazed across 1.4 million acres of land
[00:20:54] that's around the size of the entire state of Delaware. That's 70 times bigger than the previous record,
[00:21:01] and 50 times the area of all the fires over the previous 15 years combined.
[00:21:07] So what was so special about the 1988 fires? Well, to find out, we made a forest fire simulator.
[00:21:13] - We've got a grid of squares, and on each square, either a tree could be there,
[00:21:19] it could grow, or it could not be there. There's gonna be some probability for lightning strikes. So you know, the higher that probability,
[00:21:26] the more fires we're gonna have. We can run this. - So trees are growing, trees are growing,
[00:21:32] forest is filling in, nice, getting pretty dense.
[00:21:38] - What do you expect is gonna happen? - I expect to see some fires probably,
[00:21:44] you know, now that, oh, that was good, that was a good little fire. Whoa, whoa,
[00:21:54] no way. Well, that's crazy. You haven't adjusted the parameters, right? It is just like,
[00:22:02] - Not yet. Not yet. - This seems like a very critical situation just by itself.
[00:22:07] I say that because of how big that fire was. - This sort of system will tune itself to criticality,
[00:22:14] and you can, you can see it start to happen. So right now, I think it's a good moment where you have basically domains of a lot
[00:22:20] of different sizes. And then one way to think about it is, if some of these domains become too big,
[00:22:26] then you get a single fire like that one perfectly timed, burns them out, it's just gonna propagate throughout the
[00:22:32] whole thing and burn it back down a little. But then if it goes too hard, then now you've got all these domains
[00:22:37] where there are no trees, and so it's gonna, you know, grow again to bring it back to that critical state. - I can see how it's the feedback mechanism, right,
[00:22:45] that the fire gets rid of all the trees and there's nothing left to burn, and then that has to fill in again.
[00:22:51] - Yeah - Yeah. But if there hasn't been a fire, then the forest gets too thick and then it's ripe for this sort of massive fire.
[00:23:00] - For a magnet. You have to painstakingly tune it to the critical point, but the forest naturally drives itself there.
[00:23:06] This phenomenon is called self-organized criticality. And if you let it run, what you get is again
[00:23:13] a power law distribution. So this is log log, so it should be a straight line. - That kind of stuff seems so totally random
[00:23:22] and unpredictable, and it is in one way, and yet it follows a pattern. There's a consistent mathematical pattern
[00:23:28] to all these kind of disasters. It's, it's shocking. - Is there something fractal about this?
[00:23:36] - Mostly in terms of the, I guess, domains of the trees when you're at that critical state.
[00:23:42] So you get very dense areas, you get non dense areas, and as a result, when a single lightning bolt strikes,
[00:23:48] you can get fires of all sizes. Most often you get small fires of 10 or fewer trees burning a little less frequently.
[00:23:55] You get fires of less than a hundred trees. And then every once in a while you get these massive fires
[00:24:01] that reverberate throughout the entire system. Now you might expect that because the fire is so large, there has
[00:24:07] to be a significant event causing it. But that's not the case because the cause for each fire is the exact same.
[00:24:13] It's a single lightning strike. The only difference is where it strikes and the exact makeup of the forest at that time.
[00:24:21] So in some very real way, the large fires are nothing more than magnified versions of the small ones.
[00:24:27] And even worse, they're inevitable. So what we've learned is that for systems in a critical state,
[00:24:32] there are no special events causing the massive fires. There was nothing special about the Yellowstone fire.
[00:24:39] - In 1935, the US Forest Service established the so-called 10:00 AM policy.
[00:24:44] The plan was to suppress every single fire by 10:00 AM on the day following its initial report.
[00:24:49] Now, naively, this strategy makes sense. I mean, if you keep all fires under strict control,
[00:24:54] then none can ever get out of hand. But it turns out this strategy is extremely risky.
[00:25:01] - So let's say we're gonna bring down the lightning probability, so it's very small,
[00:25:06] only one in a million right now. And we're also gonna crank up, you know, the tree growth a little bit.
[00:25:12] Now, what do you think is gonna happen? - We're gonna get some big fires I would imagine, like a lot
[00:25:18] of not fire and then some huge fires. Yeah.
[00:25:25] - Yep. - Oh boy. So nowadays the fire service has a very different approach.
[00:25:30] They acknowledge that some fires are essential to make the mega fires less likely. So they let most small fires burn
[00:25:36] and only intervene when necessary. In some cases, they even intentionally create small fires
[00:25:42] to burn through some of the buildup. Though it could take years to return the forest to its natural state after a century of fire suppression.
[00:25:49] But it's more than just the Earth's forests that are balanced in this critical state.
[00:25:54] Every day the Earth's crust is moving and rearranging itself. Stresses build up slowly as tectonic plates rub against each other.
[00:26:02] Most of the time you get a few rocks crumbling, the ground might move just a fraction of a millimeter,
[00:26:07] but the stresses dissipate in many earthquakes that you wouldn't even feel. - There are really tiny earthquakes
[00:26:13] that are happening right now between be beneath your feet, you just can't feel 'em. 'cause they're very small, but they are earthquakes.
[00:26:20] They're driven by small slipping movements in the Earth's crust. - But sometimes those random movements can trigger a
[00:26:27] powerful chain reaction. - In Kobe Japan, the morning of January 17th, 1995 seemed just like any other,
[00:26:35] this was a peaceful city. And although Japan as a country is no stranger to earthquakes, Kobe hadn't suffered a major
[00:26:41] quake for centuries. Generations grew up believing the ground beneath them was stable.
[00:26:46] But that morning, deep underground, a stress released nearby the Nojima fault line.
[00:26:51] The stress propagated to the next section of the fault. And the next, within seconds, the ruptured cascaded along 40 kilometers of crust,
[00:26:59] shifting the ground by up to two meters and releasing the energy equivalent of numerous atomic bombs.
[00:27:05] The resulting quake destroyed thousands of homes along with most major roads and railways leading into the city.
[00:27:10] It killed over 6,000 people and forced 300,000 from their homes.
[00:27:16] - How far it goes depends a lot on chance and the organization of all that stress field in the Earth's crust.
[00:27:23] And it just seems to be organized in such a way that it is possible oftentimes for the earthquake
[00:27:29] to trickle along an avalanche along a long way and produce a very large unusual earthquake.
[00:27:35] But if you look at the process behind that earthquake, it is exactly the same physical process.
[00:27:40] It's just that the earthquake generating process naturally produces events that range over an enormous range of scale.
[00:27:47] And we're not really used to thinking about that. - We have this ingrained assumption that we can use the past
[00:27:53] to predict the future, but when it comes to earthquakes or any system that's in a critical state,
[00:27:58] that assumption can be catastrophic because they're famously unpredictable. So how can you even begin
[00:28:04] to model something like the behavior of earthquakes? - In 1987, Danish physicist Per Bak
[00:28:09] and his colleagues considered a simple thought experiment, take a grain of sand and drop it on a grid, then keep dropping grains on top
[00:28:17] until at some point the sand pile gets so steep that the grains tumble down onto different squares.
[00:28:23] - What they looked at was the size of these, what they were calling avalanches, these reorganizations
[00:28:30] of numbers of grains of sand. They asked for how often do you see avalanches of a certain size?
[00:28:36] - This is the most simple version of a sand pile simulator that you could almost imagine.
[00:28:41] We're gonna drop a little grain of sand, at first always in the center, and then it's just gonna keep going up for one grain,
[00:28:48] it'll be fine for two grains, it'll be fine, three grains, it'll be fine, but it's on the edge of toppling. And then when it reaches four
[00:28:54] or more, it's gonna basically go, it feels a bit like a,
[00:29:00] I don't know, pulsing thing, like something's trying to escape or something very video game-like
[00:29:05] that seemed pretty crazy and it is symmetrical. - Yeah, nice geometric features.
[00:29:11] - So this might be interesting because right now we paused it at a point where this middle one is gonna go
[00:29:17] and then you look around it and you see essentially you can think of these
[00:29:23] brown or you know, these three tall grain stacks
[00:29:29] as being maximally unstable. They're about to go. And so you could think of them as these fingers
[00:29:35] of instability, if anything touches them. The whole system, like they're, they're just gonna go,
[00:29:42] - I see it propagating out, - It's cool seeing it slower. I feel like you can see several waves
[00:29:50] propagating at the same time. - Some people have reasoned that the earth's crust becomes riddled with similar fingers of instability
[00:29:57] where you get stresses building up and then when one rock crumbles, it can propagate along these fingers potentially triggering
[00:30:04] massive earthquakes. If you look at the data, there's some even more compelling evidence
[00:30:09] that links the sand pile simulation to earthquakes. - Let's say instead of dropping it at the center,
[00:30:15] pretty unrealistic to have a drop in the center. I'm gonna drop at random.
[00:30:22] - Huh. That is crazy. You can actually see it tune itself to the critical state.
[00:30:30] Like at the start, you only see these super tiny avalanches. - Yeah. - And then now it's everything.
[00:30:36] - It has to build up. - We can slow down a little.
[00:30:42] Oh, and that's a super clean power law. There are events of all sizes.
[00:30:47] One grain of sand might knock over just a few others, or it could trigger an avalanche of millions of grains
[00:30:53] that cascade throughout the entire system. And if you look at the power law you get from the sand pile
[00:30:59] simulation, it closely resembles the power law of the energy released by real earthquakes.
[00:31:05] But if you look at the sand pile experiment more closely, it doesn't just resemble earthquakes.
[00:31:10] What does it remind you of? - Forest fires. - Right?! Feels like it's the exact same behavior.
[00:31:16] - That's the really surprising thing. And that's why this little paper with a sand pile was published in the world's top journal
[00:31:23] because it did something that people just didn't really think was was possible. - Now, what's ironic is if you look at real sand piles,
[00:31:31] they don't behave like this. - Okay, you said sand, I'm gonna do an experiment on a real sand pile.
[00:31:37] And of course it doesn't follow a power law distribution of avalanches at all. It's totally wrong.
[00:31:44] Per Bak naturally gets a chance to reply to the criticism. And he says, I'm pretty close to quoting.
[00:31:52] He says, self-organized criticality only applies to the systems it applies to.
[00:31:58] So he doesn't care the, the fact that his theory is not relevant to real sand piles. So what? Get out of my face.
[00:32:05] He's interested in bigger fish to fry than, than, you know, sand piles. It's like you're taking me too, literally.
[00:32:12] I'm talking about a universal mechanism for generating power laws. And the fact that it doesn't depend,
[00:32:17] it doesn't work in real sand is uninteresting to him. I thought that took some real nerve.
[00:32:22] - You could think about the earth and the earth going around the sun.
[00:32:28] That's a very complex system. You've got all the, you've got the molten core, everything sloshing around, and you've got oceans
[00:32:34] and you've even got the moon going around the earth, which in theory, you know, all should affect the exact motion
[00:32:40] of the earth around the sun. But Newton ignored all of that. All he looked at was just a single parameter,
[00:32:47] essentially the mass of the earth. And with that, he could correctly, for the most part, predict how the earth was gonna go around the sun.
[00:32:54] Similarly here, there are people that have looked at these phenomena that go to the critical state in this,
[00:33:00] in this case it's self-organized criticality as it brings itself there. And what they find is that there's this universal behavior
[00:33:07] where it doesn't even really matter what the sub parts are, you just get the behavior that's the exact same
[00:33:14] - At that critical point when, when all the forces are poised and the system is right on that delicate balance
[00:33:21] between being organized, highly organized, or being totally disorganized, it turns out that almost none
[00:33:27] of the physical details about that system matter to how it behaves.
[00:33:33] There's just a universal behavior that is irrespective of what physical system you're talking about.
[00:33:39] The term that was used is called universality. And it's kind of a miracle. It means you can make extremely powerful theories without
[00:33:47] involving any technical details, any real details of the material. - What this means is that you could have these systems
[00:33:54] that on the surface seem totally different, but when you get to the critical point, they all behave in the exact same way.
[00:34:01] The other thing you could do is instead of this being trees, you could imagine it being people.
[00:34:07] And the thing that's spreading... - Is disease. - Is disease, yeah.
[00:34:12] - You almost get something for nothing at these, at these critical points. - See, many of these systems fall into what's known
[00:34:18] as universality classes. Some of them you need to tune to get there like magnets at their Curie temperature
[00:34:24] or fluids like water or carbon dioxide at their critical points. But some other systems seem to organize themselves
[00:34:31] to criticality like the forest fires or sand piles or earthquakes. But what's crazy is
[00:34:37] that if you succeed in understanding just one system from a class, then you know how all the systems in
[00:34:43] that class behave. And that includes even the crudest simplest toy models like
[00:34:48] the simulations we've looked at. So you can model incredibly complex systems with the most basic of models.
[00:34:55] And some people think this critical thinking applies even further. When we look around the world, there are lots of systems
[00:35:01] that show the same power law behavior that we see in this critical systems. It's in everything from DNA sequencing to the distribution
[00:35:09] of species in an ecosystem to the size of mass extinctions throughout history. We even see the same behavior in human systems like the
[00:35:17] populations of cities fluctuations in stock prices, citations of scientific papers,
[00:35:22] and even the number of deaths in wars. So some people argue that these systems
[00:35:27] and perhaps many parts of our world also organize themselves to this critical point.
[00:35:32] - So the fact that all these natural hazards, as they call them, floods, wildfires, and earthquakes, they all follow power law distributions
[00:35:40] means that these extreme events are much more common than you would think based on normal
[00:35:46] distribution thinking. - If you find yourself in a situation or an environment that is sort of governed by a power law,
[00:35:54] how how should you change her behavior? - If you have events with one of these power distributions,
[00:36:00] what you're seeing most of the time is small events. And this can lull you into a false sense of security.
[00:36:08] You think you understand how things are going. You know, floods for example, there are a lot of small floods, and then every once in a
[00:36:13] while there's a huge one. One response to this is insurance. That insurance is designed precisely
[00:36:21] to protect you against the large rare events that would otherwise be very bad. But then there's the other side of that picture,
[00:36:29] which is you are the insurance company that needs to insure people and they have a particularly difficult job
[00:36:35] because they have to be able to say how much to charge so that they have enough money
[00:36:40] to pay out when the big bad thing comes along. - In 2018, a forest fire tore through Paradise California.
[00:36:47] It became the deadliest and most destructive fire in the state's history. But the insurance company, Merced Property
[00:36:53] and Casualty hadn't planned for something that huge and when the claims came in,
[00:36:58] they just didn't have the reserves to pay out. So just like that, the company went bust.
[00:37:04] - But while extreme events can cripple some companies, there are entire industries that are built on power law distributions.
[00:37:12] Between 1985 and 2014, private equity firm, Horsley Bridge invested in 7,000 different startups
[00:37:20] and over half of their investments actually lost money. But the top 6% more than 10x in value
[00:37:26] and generated 60% of the firm's overall profit. In fact, the best venture capital firms often have more
[00:37:32] investments that lose money. They just have a few crazy outliers that show extraordinary growth.
[00:37:38] A few outliers that carry the entire performance. In 2012, Y Combinator calculated at 75%
[00:37:45] of their returns came from just two out of the 280 startups they invested in. So venture capital is a world
[00:37:52] that depends on taking risks in the hope that you'll get a few of these extreme outliers which
[00:37:57] outperform all of the rest of the investments combined. - Book publishers operate in a similar fashion,
[00:38:03] most titles flop, but in 1997, a small independent UK publisher called Bloomsbury took a
[00:38:09] chance on a story about a boy wizard. The boy's name of course was Harry Potter. And now Bloomsbury is a globally recognized brand.
[00:38:18] We see a similar pattern play out on streaming platforms. On Netflix, the top 6% of shows account for over half
[00:38:24] of all viewing hours on the platform. On YouTube, less than 4% of videos ever reach 10,000 views,
[00:38:30] but those videos account for over 93% of all views. - All these domains follow the same principle
[00:38:37] that Pareto identified over 100 years ago, where the majority of the wealth goes to the richest few.
[00:38:43] The entire game is defined by the rare runaway hits. - But not every industry can play this game.
[00:38:50] Like if you're running a restaurant, you need to fill tables night after night. You can't have one particularly busy summer evening
[00:38:56] that brings in millions of customers to make up for a bunch of quiet nights. Over a year the busy nights and quiet ones balance out
[00:39:02] and you're left with the average. Airlines are similar, an airline needs to fill seats on each flight.
[00:39:08] You can't squeeze a million passengers onto one plane. So it's the average number of passengers over the year
[00:39:13] that defines an airline success. - We're used to living in this world of normal distributions. And you act a certain way.
[00:39:20] - Yeah - But as soon as you switch to this realm that is governed by a power law, you need to start acting vastly different.
[00:39:26] It really pays to know what kind of world you're or what kind of game you're playing. - That is good. That's good. Yes.
[00:39:32] You should come on camera and just say that just like that. You were on camera, you just did do it.
[00:39:39] - If you are in a world where random additive variations can slow out over time, then you get a normal distribution.
[00:39:44] And in this case, it's the average performance. So consistency, which is important.
[00:39:50] But if you are in a world that's governed by a power law where your returns can multiply and they can grow over many orders of magnitude,
[00:39:57] then it might make sense to take some riskier bets in the hope that one of them pays off huge. In other words, it becomes more important
[00:40:04] to be persistent than consistent. - Though as we saw in the second coin game, totally random multiplicative returns give you a logged
[00:40:11] normal distribution, not a power law. To get a power law, there must be some other mechanism at play.
[00:40:18] In the early two thousands, Albert-László Barabási was studying the internet, and to his surprise, he found that there was no normal
[00:40:25] webpage with some average number of links. Instead, the distribution followed a power law.
[00:40:30] A few sites like Yahoo had thousands of times more connections than most of the others.
[00:40:36] Barabási wondered what could be causing this power law of the internet. So he made a simple prediction.
[00:40:41] As new sites were added to the internet, they were more likely to link to well-known pages.
[00:40:46] To test this prediction, he and his colleague Réka Albert ran a simulation. They started with a network of just a few nodes,
[00:40:53] and gradually they added new nodes to the network with each new node more likely to connect to those with the most links.
[00:41:00] As the network grew, a power law emerged. The power was around negative two, which almost exactly matched the real data of the internet.
[00:41:08] - Look at that. It's still so satisfying. - That's fun. This will basically also distribute a power law.
[00:41:15] One of the ideas here is that, you know, this could be individuals or even companies. And so if you're more likely to become more successful
[00:41:23] or more well known to, well more known or successful, you already are, you're gonna get this sort of runaway effect where you're, you get a few that sort
[00:41:30] of dominate, you know, the distributions. I wonder if part of the takeaway is like if you're playing
[00:41:35] some sort of game that is dominated by power law, then you better do the work as much of it
[00:41:41] as early as possible. So you get to benefit from the snowball effect, essentially. - Yeah, I guess. I guess that's, that's a good idea.
[00:41:48] I'm not sure whether you can control it though. Human beings like to think of ourselves as being a bit special and that maybe somehow
[00:41:55] because we're intelligent and have free will, we will escape
[00:42:01] the provenance of the laws of of physics in order and organization.
[00:42:06] But I think that's probably not not the case. So if you look at, at the number of world wars,
[00:42:12] and if you make a crude measure of how big is the world war by how many people it kills, which is a bit macabre,
[00:42:19] but still you find that, again, it follows a power law virtually identical to the power law you find in
[00:42:25] stock market crashes. - So if the world is shaped by power laws, then it feels like we're poised in this kind
[00:42:32] of critical state where two identical grains of sand, two identical actions can have wildly different effects.
[00:42:40] Most things barely move the needle, but a few rare events totally dwarf the rest. And that I think is the most important lesson.
[00:42:47] If you choose to pursue areas governed by the normal distribution, you can pretty much guarantee average results.
[00:42:54] But if you select pursuits ruled by power laws, the goal isn't to avoid risk, it's to make repeated intelligent bets.
[00:43:00] Most of them will fail, but you only need one wild success to pay for all the rest.
[00:43:06] - And the thing is that beforehand you cannot know which bed it's going to be because the system is
[00:43:11] maximally unpredictable. It could be that your next bet does nothing. It could do a little bit or it could change your entire life.
[00:43:18] In fact, around three years ago, I was reading this little book, and in the book there was this little line saying something
[00:43:23] like one idea could transform your entire life. So right underneath that, I wrote,
[00:43:30] send an email to Veritasium. A couple days later, I wrote an email to Derek saying, Hey Derek, I'm Casper.
[00:43:36] I study physics and I can help you research videos. I didn't hear back for four weeks, so I was getting pretty sad
[00:43:42] and just wanted to forget about it and move on. But then a couple days later I got an email back saying,
[00:43:49] Hey Casper, we can't do an internship right now, but how would you like to research, write
[00:43:54] and produce a video as a freelancer? So I did, and that's how I got started at Veritasium.
[00:44:04] Hey, just a few quick final things. All the simulations that we used in this video we'll make available for free
[00:44:10] for you to use in the link in the description. And the other thing is that we just launched the
[00:44:16] official Veritasium game. It's called Elements of Truth, and it's a tabletop game with over 800 questions.
[00:44:22] It's the perfect way to challenge your friends and see who comes out on top. Now at Veritasium, we're all quite competitive,
[00:44:30] so every time we play things get a little bit heated, but that's honestly a big part of the fun.
[00:44:35] Now, when we launched on Kickstarter, we got a lot of questions asking if we could ship to specific countries.
[00:44:42] And originally we didn't enable this, and this is our mistake. This is on us and we totally hear you.
[00:44:48] But I'm glad to say that right now we have enabled worldwide shipping. So no matter where you are in the world,
[00:44:54] you can get your very own copy. To reserve your copy and get involved. Scan this QR code or click the link in the description.
[00:45:02] I wanna thank you for all your support and most of all, thank you for watching.