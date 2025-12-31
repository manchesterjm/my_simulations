[00:00:00] Hey there, I'm Nmiz and I like to make
[00:00:02] games. But beyond games, I'm a big fan
[00:00:04] of simulations. Whether it's a physics
[00:00:06] engine, fluid sim, or voids, I've just
[00:00:09] always been a massive fan of using code
[00:00:11] to try to recreate some aspect of the
[00:00:13] real world. One of my favorite kinds of
[00:00:15] simulation is the falling sand game.
[00:00:17] You've probably come across one of these
[00:00:19] before. They used to be pretty common
[00:00:21] online, and recently they've also had a
[00:00:23] resurgence because of the game Noita. A
[00:00:25] few years ago, I made one of these
[00:00:27] falling sand games in Unity and uploaded
[00:00:29] a video about it as the first video on
[00:00:31] my channel. It's since steadily gotten
[00:00:34] more and more views, which means more
[00:00:36] and more people have gotten to see the
[00:00:37] truth. The code for that project was
[00:00:39] awful. I could barely get the simulation
[00:00:42] running at 30fps on 120x 68 pixel
[00:00:46] screen, but I've learned a lot since
[00:00:48] then. So, today I'm going to redeem
[00:00:50] myself by making a blazingly fast
[00:00:52] falling sand [music] simulation.
[00:01:00] Now, before we can optimize the hell out
[00:01:02] of this project, we first need to
[00:01:04] understand exactly how it works. The
[00:01:06] algorithm for falling sand is a type of
[00:01:08] algorithm called a cellular automaton.
[00:01:11] Essentially, that just means that every
[00:01:13] grain of sand is a cell in a grid that
[00:01:15] has a predefined rule set that tells it
[00:01:17] how to behave. Famously, to make sand,
[00:01:20] you only need three rules. First, if the
[00:01:22] pixel below the current sand cell is
[00:01:24] empty, move there. Second, if that pixel
[00:01:27] is blocked, but the pixel below and to
[00:01:29] the right is empty, move there. And
[00:01:31] finally, if both the pixels to the right
[00:01:33] and underneath the current cell are
[00:01:35] blocked, but there's room to the left,
[00:01:37] move there. With these deceptively
[00:01:39] simple rules, we get some really nice
[00:01:41] behavior, and the sand forms these
[00:01:43] pleasing triangular piles. The problem
[00:01:46] becomes clear though when we consider
[00:01:48] that to do this calculation for every
[00:01:50] sand cell on screen, we have to loop
[00:01:52] over every single cell in the grid,
[00:01:54] checking its neighbors, and only once
[00:01:56] we're done can we move on to the next
[00:01:58] cell. This is very slow because if we
[00:02:01] want to use a larger grid, for example,
[00:02:03] the grid of all pixels on a 1280x 720p
[00:02:06] monitor, we'd have to loop through over
[00:02:08] 9 million cells and do the calculations
[00:02:10] sequentially on each of them. There are
[00:02:13] a few solutions to this problem, but the
[00:02:15] one I want to try to implement is called
[00:02:17] parallelization.
[00:02:19] Basically, instead of doing our
[00:02:21] algorithm on each cell one at a time,
[00:02:23] what if we could do the calculation for
[00:02:25] all of them at once? We'd get a massive
[00:02:27] performance increase. [music] The only
[00:02:29] problem is that in general, computers
[00:02:31] are designed to work sequentially. The
[00:02:33] CPU isn't really built for this kind of
[00:02:36] parallel programming. Luckily, modern
[00:02:39] computers have another unit which is an
[00:02:41] expert at this exactly, the GPU. The GPU
[00:02:45] is responsible for rendering graphics,
[00:02:47] and so it has to do calculations for
[00:02:49] every pixel on the screen all the time.
[00:02:52] The only trade-off [music] is that
[00:02:53] writing code for the GPU is generally a
[00:02:56] bit more difficult and less intuitive
[00:02:57] than CPU code. This kind of program for
[00:03:00] the GPU is called a compute shader. We
[00:03:03] can give the computator some list of
[00:03:05] data and it'll run the same calculation
[00:03:07] on a bunch of the items in that list in
[00:03:09] [music] parallel. Obviously speeding up
[00:03:11] runtime to a pretty insane degree. The
[00:03:13] language you use to write comput shaders
[00:03:15] in Unity is called HLSL. And when using
[00:03:18] it, you get access to a lot less of the
[00:03:20] features of a modern programming
[00:03:22] language in return for a massive boost
[00:03:24] in speed. To give a simple example, say
[00:03:27] we have a list of integers. If we want
[00:03:29] to increment each of the numbers in this
[00:03:31] list by one, if we were writing this
[00:03:33] sequentially, we'd step through the
[00:03:34] list, adding one to the current element
[00:03:36] and then moving to the next. Writing
[00:03:39] this as a computator, we might send the
[00:03:41] list to the GPU, assigning a single GPU
[00:03:43] thread to each element, which will then
[00:03:45] let us add one to each element in this
[00:03:47] list at the [music] same time. We could
[00:03:50] then read back that data to the CPU and
[00:03:52] do with it what we want. So I started
[00:03:55] implementing the SAND algorithm as a
[00:03:56] computator. My first attempt was
[00:03:59] actually quite [music] similar to the
[00:04:00] CPU version. My code runs for every
[00:04:03] pixel in a texture, checking the pixel
[00:04:05] below and the pixels to the left and
[00:04:07] right and moving the current pixel
[00:04:08] accordingly. This already worked quite
[00:04:11] well. We can increase our grid size to
[00:04:12] [music] 1024x 576 and the simulation is
[00:04:16] still running incredibly fast.
[00:04:18] Performance boost achieved.
[00:04:20] Unfortunately, there are a few problems.
[00:04:22] first because the sand checks the pixel
[00:04:23] [music] below and to the right of it
[00:04:25] before the one to the left. The sand is
[00:04:27] biased to the right and our sand piles
[00:04:29] are looking uneven. This is pretty
[00:04:31] easily solved by just alternating
[00:04:33] checking the left first or the right
[00:04:34] first each frame. But now a more
[00:04:36] pressing issue becomes clear. Where's
[00:04:38] all our sand disappearing off to? We
[00:04:40] seem to be dropping a lot more sand than
[00:04:42] ends up in our piles. The reason this is
[00:04:45] happening is because of an incredibly
[00:04:46] common and interesting issue that arises
[00:04:48] in parallel programming. Race
[00:04:50] conditions. A race condition is a type
[00:04:53] of bug that occurs when your code will
[00:04:55] have a different result depending on the
[00:04:57] timing of some external uncontrollable
[00:04:59] factor. In parallel programming, this
[00:05:02] happens when two threads are trying to
[00:05:03] write to the same piece of data. We
[00:05:06] can't control which thread will execute
[00:05:07] [music] first or if they'll execute at
[00:05:09] the same time. So, unexpected behavior
[00:05:12] can pop up. In our sand simulation, this
[00:05:14] is occurring in situations like this.
[00:05:17] Pixel 1 and Pixel 2 both read Pixel 3 as
[00:05:20] empty and so they both try to move to
[00:05:22] it. So now we're left with four sand
[00:05:24] cells where we originally had five. This
[00:05:26] is of course a pretty big problem as the
[00:05:28] chemists might start getting mad at us
[00:05:30] if we casually break the law of
[00:05:31] conservation of matter. Fixing this race
[00:05:34] condition wasn't a trivial problem at
[00:05:35] all. When I was looking for solutions to
[00:05:37] this, I at some point asked chat GPT for
[00:05:39] help and it offered the novel idea to
[00:05:41] check the pixels in an alternating grid
[00:05:43] pattern so neighboring pixels wouldn't
[00:05:45] do the calculation at the same time. I
[00:05:48] thought this was interesting, so I
[00:05:49] implemented it. But the results were not
[00:05:52] quite what I had in mind. I eventually
[00:05:53] stumbled across the concept of atomic
[00:05:56] operations. Atomic in this case
[00:05:58] hearkening back to the Greek word
[00:06:00] atomos, meaning indivisible. This is
[00:06:02] because atomic operations are
[00:06:04] uninterruptible. If two threads try to
[00:06:07] do an atomic operation on the same piece
[00:06:09] of data, the operations will happen in
[00:06:11] sequence like we [music] would expect
[00:06:13] without getting in the way of each
[00:06:14] other. My solution to our race condition
[00:06:17] used an atomic operation called
[00:06:19] interlocked compare exchange, which
[00:06:21] simply compares some value with another,
[00:06:23] and if they're equal, it replaces the
[00:06:25] first value with some third arbitrary
[00:06:27] value. If you're interested to
[00:06:29] understand how this fixes our problem,
[00:06:30] here's the solution I came up with.
[00:06:32] First, I keep track of a second grid,
[00:06:34] which I call claims, that starts
[00:06:36] completely empty at the beginning of
[00:06:38] each simulation step. Then, if a thread
[00:06:40] finds that it should set a certain pixel
[00:06:42] to sand, it first runs the interlocked
[00:06:45] compare exchange. If the claims grid is
[00:06:47] empty at the slot we want to put sand,
[00:06:49] we claim that slot, filling it in for
[00:06:51] this frame. If the slot is already
[00:06:53] claimed, then we know we can't [music]
[00:06:55] set that slot to sand without losing a
[00:06:57] particle. This fairly intuitive fix
[00:06:59] solved the race condition entirely.
[00:07:01] We're no longer erasing matter from
[00:07:03] existence, and the piles are looking
[00:07:04] really nice. A small side effect of this
[00:07:06] is that on a really big grid, the sand
[00:07:09] rolls down hills pretty slowly, as it's
[00:07:11] taking extra care not to get in its own
[00:07:13] way. A little annoyed by this, I tried
[00:07:15] to find a solution. I sat for hours and
[00:07:18] the best idea I could come up with was
[00:07:20] stepping the simulation twice each frame
[00:07:21] of the game, which actually did help a
[00:07:24] little. But the real solution came when
[00:07:26] I looked at how Powder Toy, maybe the
[00:07:28] most famous Falling Sand simulation,
[00:07:30] handles this. The answer, it doesn't.
[00:07:32] Sand Cascades pretty slowly there, too.
[00:07:35] After checking some other games, it
[00:07:37] seems like nearly every single Falling
[00:07:39] Sands Sim has this detail. So, like the
[00:07:41] amazing programmer I am, I declared it a
[00:07:43] feature, not a bug, and moved on. Now
[00:07:45] that the sand was working, I decided it
[00:07:47] was time for a visual upgrade. I first
[00:07:50] made the sand color randomly interpolate
[00:07:52] between a dark and a bright color, which
[00:07:54] did look much better. But I then had the
[00:07:56] idea to make the sand you place smoothly
[00:07:58] transition between two colors based on
[00:08:00] time. I really like this combination.
[00:08:03] The red and orange sand looks almost
[00:08:05] fiery to me, which I really like. I
[00:08:07] couldn't resist making it alternate
[00:08:09] between any number of colors. And here's
[00:08:11] the result of that. [music]
[00:08:18] All in all, I'm incredibly proud of how
[00:08:20] this project turned out. My rough
[00:08:22] estimation for how much we increased the
[00:08:24] performance by relative to the version I
[00:08:26] made a few years ago is a factor of
[00:08:28] 2,000, which I think is pretty
[00:08:30] remarkable. I also looked through the
[00:08:32] original codebase when preparing for
[00:08:34] this project and found some absolutely
[00:08:36] absurd decisions. So, I really feel like
[00:08:38] I've improved as a programmer since
[00:08:40] then. To any programmers or game
[00:08:41] developers watching, I definitely
[00:08:43] recommend remaking your old projects
[00:08:45] with optimization in mind.
[00:08:50] Thanks so much for watching. I'm sorry
[00:08:52] for the long break between videos. This
[00:08:53] one took a while to make and I've had
[00:08:55] some more pressure from university. I'll
[00:08:57] be back to making semi-regular videos
[00:08:59] now, so be sure to subscribe if you
[00:09:01] enjoy this type of content. Check out my
[00:09:03] Patreon for exclusive early access to my
[00:09:05] projects, a choice on what video I'll
[00:09:07] make next, and more perks. and it really
[00:09:09] is the best way to support me.
[00:09:11] Otherwise, just leave a like, comment
[00:09:13] your thoughts on the video and what
[00:09:14] you'd like to see next. Until next time,
[00:09:16] see you.