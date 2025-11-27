[00:00:00] I thought we'd um go back to a bit of
[00:00:02] basics and talk about memorization or as
[00:00:04] I like to call it caching things. Um
[00:00:07] it's it's an interesting and useful
[00:00:09] technique in programming and one that
[00:00:11] perhaps people sometimes kind of don't
[00:00:12] really understand what it is. It's
[00:00:14] actually quite simple. Um and so I I
[00:00:17] thought the way to do this would be to
[00:00:18] pick a problem that can be helped with
[00:00:20] memorization depending on how you
[00:00:22] implement it and and then we'll see what
[00:00:24] it does.
[00:00:27] So, there was a lovely number file video
[00:00:29] on frog hopping.
[00:00:30] Now, if we have two lily pads, we could
[00:00:33] go one and then one, or we could go two,
[00:00:36] which is a problem I've come across
[00:00:37] before, but it's always nice to see the
[00:00:38] mathematical derivation of this. Note
[00:00:40] that there won't be any such things in
[00:00:41] this video. I'm going to program it.
[00:00:43] Will those frogs be on stilts?
[00:00:45] Frogs on stilts?
[00:00:46] No. No regular frogs. Actually, I was
[00:00:48] very impressed with Brady's animations.
[00:00:50] The idea is you've got some number of
[00:00:52] lily pads or stones or something that
[00:00:54] frogs are hopping on and they can hop
[00:00:55] one at a time or two at a time and
[00:00:58] you've got, you know, let's say 10
[00:00:59] stones. How many different combinations
[00:01:01] of types of hops would would it require
[00:01:04] to get to the end? So let's say one one
[00:01:06] one two or two hops and then one one,
[00:01:09] right? It turns out that it's related to
[00:01:12] Fibonacci sequence. Fibonacci is a very
[00:01:14] common example of something you can use
[00:01:16] recursion to solve not unwisely
[00:01:17] sometimes. Right? So I thought we'd
[00:01:19] perhaps make the problem a little bit
[00:01:21] more complicated just to make it a bit
[00:01:22] more interesting, right? And also there
[00:01:24] is already a great number file video on
[00:01:25] this. So we're going to do stair
[00:01:27] climbing. You know those things in your
[00:01:28] house that are tiring to go up. Let's
[00:01:30] imagine you have some number of stairs,
[00:01:32] right? So let's say 1 2 3 4 5 6 8 9 10.
[00:01:38] I think that's 10 stairs. Why is the
[00:01:40] last one round?
[00:01:41] It's carpet.
[00:01:41] Yeah, round a carpet. Now you can climb
[00:01:43] up. Sometimes you could skip a stair or
[00:01:45] you could skip up three stairs. If you
[00:01:46] really got good legs, you could jump
[00:01:48] four or five stairs, right? I can't. Um,
[00:01:50] or you can just be regular and climb one
[00:01:52] stair at a time. So, we've got n stairs.
[00:01:55] Let's say n stairs. And we can go in
[00:01:58] some number. It's, you know, let's say a
[00:02:01] set of 1, three, or five stairs at a
[00:02:04] time. Right? So, we can go from here up
[00:02:07] one stair or we can go up one, two,
[00:02:10] three stairs or we can jump 1 2 3 4 5
[00:02:12] which looking at it is quite a long way.
[00:02:14] um you can just just jump half the half
[00:02:16] the staircase. How many different ways
[00:02:18] could you climb these stairs? It's a
[00:02:20] very similar problem to the frog hopping
[00:02:23] problem. Um it's just a slightly more
[00:02:25] interesting implementation when we code
[00:02:26] it up, right? And so I won't be driving
[00:02:28] the maths. I'm going to brute force it
[00:02:30] using my laptop. Let's think about
[00:02:32] breaking the problem down in this kind
[00:02:34] of recursive way. So let's say we're at
[00:02:36] the top, right? How did we get there?
[00:02:38] What was the last step we could have
[00:02:40] done? Right? It's one or three or five,
[00:02:43] right? So, we either came from here or
[00:02:46] we came from one, two, three here or we
[00:02:49] did this ridiculous jump 1 2 3 4 5 and
[00:02:53] we came from here. If we say, well,
[00:02:55] okay, f, which is our function we're
[00:02:57] trying to solve of n steps, right? with
[00:03:01] one, three, and five possible steps is
[00:03:03] going to be equal to however many
[00:03:05] combinations of stairs we could go here
[00:03:08] plus however many stairs combinations we
[00:03:10] could get to here plus however many
[00:03:12] combinations we could get to here.
[00:03:13] Right? It's a very similar problem. So
[00:03:15] it would be f of nus1
[00:03:19] plus f of n -3
[00:03:23] plus f of n -5. you've drawn starting at
[00:03:27] the top and will you always have to work
[00:03:29] backwards to work this out?
[00:03:30] Um, it's easier in this case. Um, it's
[00:03:33] it's better to think of it if someone's
[00:03:34] climbing the stairs, but we're kind of
[00:03:37] in hindsight reflecting on how it went,
[00:03:39] right?
[00:03:39] How could you have got there?
[00:03:40] Yeah. How could you have got there? And
[00:03:42] so, actually, if if you were doing this
[00:03:44] for frogs where you jump one or two
[00:03:45] steps, it's easier just to write a for
[00:03:47] loop that calculates a Fibonacci number,
[00:03:49] right? And and you wouldn't necessarily
[00:03:51] even need to use recursion to solve
[00:03:53] Fibonacci even though it's a nice
[00:03:54] example of it. I suppose it's a bit like
[00:03:56] when you're planning a route in in a
[00:03:58] map, you know, you need to know where
[00:03:59] you're going before you set off, don't
[00:04:01] you?
[00:04:01] If you consider that you might have very
[00:04:03] many possible step jumps, right? So,
[00:04:05] let's say you're trying to climb a 100
[00:04:07] steps, but you're some kind of athlete
[00:04:08] and you can jump eight, seven, six,
[00:04:10] five, four time at the same time. It
[00:04:12] becomes very unwieldy to try and
[00:04:15] encounter all those or try and try and
[00:04:17] consider all those possibilities from
[00:04:18] the start going upwards, right? That is
[00:04:20] going to expand. So, in a way, breaking
[00:04:23] it down into just copies of the same
[00:04:25] problem in a slightly easier way is a
[00:04:28] very natural way to do this, right? And
[00:04:29] it and it lends itself well to
[00:04:31] recursion. When you see a function like
[00:04:32] that, if you're writing in using
[00:04:34] recursion, at least naively, looks
[00:04:37] pretty easy to do. So, let's code that
[00:04:39] up and then we'll explain why that's a
[00:04:41] very bad idea.
[00:04:43] All right, so I've got a almost blank
[00:04:46] Python file here. We've got this small
[00:04:47] function that I've written where we can
[00:04:50] time how long another function takes to
[00:04:52] run. So this will allow us later to
[00:04:53] test. We're not going to that's not
[00:04:54] interesting. We're going to skip over
[00:04:56] that. What we're going to do to begin
[00:04:57] with is not worry too much about like
[00:04:59] possible combinations of steps. So 1 2 3
[00:05:01] 4 five different different steps. Let's
[00:05:03] just say we're fixing it at 1, three,
[00:05:05] and five for now, right? To make it a
[00:05:07] bit easier. So we're going to define
[00:05:08] some function define step count which is
[00:05:11] going to be for n where n is the number
[00:05:14] of steps. It's going to return a value
[00:05:16] of how many different combinations are
[00:05:17] of steps you can take given the options
[00:05:19] are one, three, or five. Right? So, we
[00:05:22] already know broadly speaking what we're
[00:05:24] going to have to do is return step count
[00:05:27] of n uh minus one plus step count of n
[00:05:32] minus 3 plus step count of n minus 5.
[00:05:37] Right? And that will workish. Right? If
[00:05:40] we run this, we will quickly find it
[00:05:43] doesn't work. Right? So uh if we say
[00:05:45] step count of 10.
[00:05:47] So step count is how many steps in
[00:05:48] total?
[00:05:49] Yeah, give me the steps in total. It's
[00:05:50] going to say ah maximum recursion depth
[00:05:52] reached because the previous line
[00:05:54] repeated 990 times. Right. The reason is
[00:05:56] because I haven't got an end condition.
[00:05:58] I haven't said what happens when we get
[00:06:00] to the bottom of the staircase.
[00:06:01] Oh, so it could go into minus numbers
[00:06:02] and just
[00:06:03] Yeah, it's just going on on some
[00:06:04] infinite staircase and it turns out my
[00:06:05] laptop isn't powerful enough. What are
[00:06:07] the end conditions? Well, if we arrive
[00:06:09] at zero, there are no more steps, then
[00:06:12] this was a successful path. We don't
[00:06:13] know what the function calls were. So,
[00:06:15] we don't know what the order of the
[00:06:16] paths were, but we know that's
[00:06:17] successful. So, if there's no brackets,
[00:06:19] I've been doing too much Java. If n
[00:06:22] equals 0, return one. Right? This is a
[00:06:26] successful path. And we add one to our
[00:06:28] total.
[00:06:28] So, to trap it in case it goes below
[00:06:30] zero.
[00:06:30] Ah, yes. So, let's imagine you're one
[00:06:33] step from the bottom. your n minus one
[00:06:35] will return zero but n minus 3 or n
[00:06:38] minus 5 are going to overshoot and those
[00:06:39] are not valid combinations of steps
[00:06:41] right so we can say if n is less than
[00:06:44] zero return n and those are our uh end
[00:06:47] conditions let's save that and let's run
[00:06:49] this and see if this runs any better
[00:06:50] than it did before so step count 10 47
[00:06:55] possible combinations right I couldn't
[00:06:57] actually off the top of my head tell you
[00:06:58] whether that's correct but let's pretend
[00:06:59] that it is now this is actually not a
[00:07:02] good implementation this is
[00:07:04] exponential growth. What essentially
[00:07:06] intuitively what's happening here is n
[00:07:08] minus one, n minus 3 and n minus 5 are
[00:07:11] computing a load of repeating versions
[00:07:14] of the same problem and it's hugely
[00:07:16] memory inefficient to do this. Right? So
[00:07:18] you'll see that if I if I call step
[00:07:20] count of 25,
[00:07:23] it's pretty fast. If it's 30, it's
[00:07:26] getting a little bit slower. If it's 35,
[00:07:28] now we're actually having to wait for a
[00:07:30] little bit for it to finish. Once it
[00:07:32] gets to 40 or 50, this laptop probably
[00:07:33] won't do it. Right. So, it's growing
[00:07:36] very, very fast because it's an
[00:07:38] explosion of different combinations of
[00:07:39] steps.
[00:07:40] So, it's just literally having to do too
[00:07:41] many, if you pardon the pun, steps.
[00:07:44] Yes, it's Yes, that's exactly right.
[00:07:46] Let's have a look at why. We're back on
[00:07:48] our paper and we're just going to look
[00:07:49] at the sort of function calls we would
[00:07:50] be doing if we were writing it this way
[00:07:52] and why that is a big big problem,
[00:07:54] right? In terms of the speed, it doesn't
[00:07:56] matter for for n equals 10, right? And
[00:07:58] so sometimes you needn't do anything
[00:07:59] extra because yes it's slow but you
[00:08:02] never have a big problem and so it's not
[00:08:03] a problem but often that is not the
[00:08:06] case. So let's just go with um f of six
[00:08:10] for now. I'm going to call it f only
[00:08:11] because if I write step count I'm going
[00:08:13] to very much run out of page very very
[00:08:15] quickly. So this is f of six.
[00:08:17] So this is a sixst step stair count.
[00:08:19] Yes. And remember for now all we can do
[00:08:22] is go in one three and five jumps. So
[00:08:24] this is going to call three functions.
[00:08:26] It's going to call n -1, n -3, n - 5. So
[00:08:30] that's going to go to f of 5, which is n
[00:08:34] minus one, f of 3. It makes me feel
[00:08:38] better when you nod, you know, my my
[00:08:39] simple arithmetic. I'm not messing up in
[00:08:41] front of everyone. Uh, and f of one,
[00:08:44] right? Because, you know, which is
[00:08:45] nearly finished. Now, let's expand this
[00:08:46] one. So f of five could be f of four, f
[00:08:50] of two and f of n which is actually our
[00:08:53] win condition but you know we we won't
[00:08:55] dwell on it. I mean I'm already running
[00:08:56] out of page this is a problem. So let's
[00:08:58] go f of three would be f of two f of n f
[00:09:03] of minus2 right which is going to be a
[00:09:05] fail condition but f of one is going to
[00:09:08] be f of n f of -2 and f of -4 these will
[00:09:14] end f of four will be f of three f of 1
[00:09:18] f of -
[00:09:21] uh one something like that you can see
[00:09:24] we're very quickly expanding and this is
[00:09:26] only f of six I already did f of 10 on
[00:09:28] here. So, you know, this is this is a
[00:09:29] big problem. I mean, let's keep going. F
[00:09:31] of of one and so on and so on, right?
[00:09:35] So, and you can imagine this is expanded
[00:09:37] very very quickly. You know, N6 if it
[00:09:39] goes bigger than this, it's going to be
[00:09:41] huge. And the other problem is we've
[00:09:43] just done all this work multiple times
[00:09:45] for absolutely no benefit at all. So, if
[00:09:47] you look at all the occurrences of let's
[00:09:49] say f of three, right? N equals 3. Here,
[00:09:51] here there's another one over here. um
[00:09:54] two is here here zero is everywhere
[00:09:58] right and this will happen more and more
[00:10:00] the bigger the tree is and the more
[00:10:01] combinations of sets you can do
[00:10:04] memorization is the idea that if we're
[00:10:06] using let's say a recursive function or
[00:10:09] a function that we're calling multiple
[00:10:10] times if for a given input the output
[00:10:13] doesn't change we can just cache that
[00:10:16] result store it and then do a very quick
[00:10:18] look up and go ah we already calculated
[00:10:20] that as five we don't need to we don't
[00:10:21] need to do it again and we can massive
[00:10:23] massively reduce the time it would take.
[00:10:26] So let's imagine that we'd already
[00:10:27] calculated this. When we get down to
[00:10:29] here, we don't need to expand it because
[00:10:31] we already have the result. That's what
[00:10:33] memorization is. Before we think about
[00:10:35] memorization and caching our
[00:10:36] intermediate results, let's just improve
[00:10:38] our step count algorithm to handle the
[00:10:40] general case of it's not always 1,
[00:10:42] three, and five steps that you're doing.
[00:10:44] Right? What we're basically doing is n
[00:10:46] minus whatever that step combination is
[00:10:49] for all the possible step combinations.
[00:10:51] So we can add a parameter. Let's call it
[00:10:54] steps and that is the different let's
[00:10:56] say 1 three and five and then we can
[00:10:58] have something like so in Python for
[00:11:01] those of you that don't use Python you
[00:11:03] can do something called list
[00:11:03] comprehension where you can say a
[00:11:06] particular step for for all of the steps
[00:11:08] in that list. So we can say s for s in
[00:11:13] steps, right? And then we're going to
[00:11:14] put this into a function. For each s,
[00:11:16] we're going to say we're going to call
[00:11:19] step count
[00:11:20] n minus s for s in steps. And then we're
[00:11:23] going to sum that, right? And Python has
[00:11:26] a lovely sum function that I don't have
[00:11:27] to bother writing. And then we're going
[00:11:28] to return that instead. So let's just
[00:11:30] test that works before we get too
[00:11:32] carried away. So I'm going to save that
[00:11:34] step count of let's say 10 steps. And we
[00:11:38] already know it's one, three, and five
[00:11:40] possible combinations missing one
[00:11:42] argument. Oh, I've forgotten to pass the
[00:11:45] steps to the to the function, right? So,
[00:11:48] let's go from there. So, let's see if
[00:11:49] this works. So, step count for let's say
[00:11:51] 10 steps and 1 3 and five possible step
[00:11:55] combinations. 47. I'm kind of pleased
[00:11:57] the answer is the same. Actually, I'll
[00:11:59] be honest with you. We can actually
[00:12:01] change it. So, we could say, okay, you
[00:12:02] can now only go one and five steps. You
[00:12:04] can't go three steps at a time. And that
[00:12:06] was actually only eight combinations,
[00:12:08] right? And you could probably work them
[00:12:09] out by hand. So it it does theoretically
[00:12:12] work. It's just going to be very very
[00:12:14] slow and very very inefficient. So let's
[00:12:16] go back to our code and think about how
[00:12:17] we could fix this. All we need to do is
[00:12:20] store a dictionary, right, which is
[00:12:24] Python's name for a kind of an array of
[00:12:27] key and values for each potential n. And
[00:12:30] when we encounter it, we just store that
[00:12:32] value and we can reference it later. I'm
[00:12:34] just going to tidy this up a bit. So,
[00:12:35] we're not going to uh override or change
[00:12:37] our step count cuz we want to be able to
[00:12:39] compare the speed of these things. So,
[00:12:40] I'm just going to copy this down here
[00:12:42] and we're going to call it memsteps. And
[00:12:44] mem is going to be some kind of
[00:12:46] memorized version, some caching version
[00:12:48] of the same thing, right? So, how would
[00:12:50] we do that? Well, we need an
[00:12:51] implementation that has a cache. So,
[00:12:54] we're going to need to create that
[00:12:54] cache. There are lots of different ways
[00:12:56] in Python you could choose to do this.
[00:12:58] I'm going to do it by having another
[00:12:59] function that has a cache as a
[00:13:01] parameter. Right? You could put it
[00:13:02] inside. You could do all kinds of clever
[00:13:04] things. For the sake of clarity, I won't
[00:13:07] do that. So, mem cache with n steps and
[00:13:11] a cache, right? And now, mem is just
[00:13:14] going to call meeps cache with n steps
[00:13:20] and an empty dictionary, which is going
[00:13:22] to be the empty cache that we're going
[00:13:24] to use. So, we don't actually call
[00:13:27] memsteps cache directly. We could, we're
[00:13:28] going to use memsteps, and then we're
[00:13:30] going to have this cached version,
[00:13:31] right? Hopefully that's nice and clear.
[00:13:33] The rest of the code is pretty similar.
[00:13:34] So how do we add our temporary cache
[00:13:37] into this function? Well, first of all,
[00:13:39] if n is zero, we're still going to
[00:13:43] return one, right? If n is less than
[00:13:45] zero, we're still going to return zero,
[00:13:47] right? That's nice and easy. There's no
[00:13:49] lookups. That's very quick. If n is in
[00:13:52] the cache, right? That's a nice uh
[00:13:55] Python way of saying, does the
[00:13:56] dictionary contain that key? Right? then
[00:13:59] we're just going to return
[00:14:01] the cache value at position n. If it's
[00:14:03] not, we actually have to do the slightly
[00:14:06] more troubling expansion. All we're
[00:14:08] going to do, so instead of just
[00:14:09] returning the sum, we're going to say
[00:14:11] total equals sum and then we're going to
[00:14:14] say cache of n is equal to total, right?
[00:14:20] And we also need to return the total.
[00:14:24] Now the only other thing is I need to
[00:14:26] update this function call because this
[00:14:27] function call is looking in the wrong
[00:14:28] place. I'm currently calling step count.
[00:14:30] I need to return I need to call
[00:14:32] memstep's cache like this right and I
[00:14:34] need to pass the cash through. All we're
[00:14:36] doing is exactly the same algorithm but
[00:14:38] this time we have access to this
[00:14:40] dictionary that is holding previous ends
[00:14:42] that we've seen before. If we come up
[00:14:44] with one we've seen before we just
[00:14:46] return that value straight away rather
[00:14:47] than actually doing all these function
[00:14:49] calls and expanding this. This is what
[00:14:51] memorization is. It's just adding this
[00:14:53] ability to recall previous versions of
[00:14:55] this function and returning those
[00:14:57] results really, really quickly rather
[00:14:59] than computing them all again from
[00:15:00] scratch. Now, it's just occurred to me
[00:15:02] that we don't actually return this value
[00:15:04] here. So, I'm just going to put a return
[00:15:06] in. I'm sure those of you were very
[00:15:08] annoyed and had spotted that already.
[00:15:10] Um, let's do some timing tests. So, I've
[00:15:13] got this time it function. So, time it
[00:15:16] and you pass the function you're trying
[00:15:18] to time. So let's say step count the
[00:15:20] number of steps 10 and the number of
[00:15:22] possible step combinations 135
[00:15:25] and the time elapse was 0 0 083 seconds
[00:15:29] not very long. Let's watch what happens
[00:15:32] as we start to increase that number. So
[00:15:33] now we're going to do 30 steps.
[00:15:37] Half a second, right? 35 steps.
[00:15:42] Well, now we're just sitting watching
[00:15:43] nothing, right? It's about Oh, hang on.
[00:15:46] Uh it will do it. Yeah. So, it's 3.7
[00:15:49] million possible combinations and it
[00:15:51] took seven and a half seconds to run.
[00:15:52] Okay.
[00:15:53] Not great. Now, let's replace the step
[00:15:56] count with our mem, right? And just
[00:15:59] remind myself what I called it.
[00:16:01] Memsteps. Yeah. Okay. Good. Me steps.
[00:16:04] 0.051
[00:16:06] seconds
[00:16:06] for that same
[00:16:07] for the same function. I can't really
[00:16:09] increase the step count test any further
[00:16:11] because my laptop won't do it. I can
[00:16:14] produce much bigger values for with
[00:16:16] memsteps because I'm caching so much of
[00:16:18] this tree. So let's say what are the
[00:16:21] possible combinations of a 100 steps in
[00:16:24] one three and five step increments and
[00:16:26] the answer is a very very big number in
[00:16:30] fractions of a second right the number
[00:16:32] is is into the quadrillions or trillions
[00:16:34] or something. It's very very large. I
[00:16:36] suggest you don't try and do it by hand
[00:16:37] on the stairs basically um or by feet in
[00:16:40] languages like this. Often libraries
[00:16:42] exist to help you with this kind of
[00:16:44] stuff. So memorization is the idea of
[00:16:47] you've got a repetitive function you're
[00:16:49] calling over and over again. You're
[00:16:51] going to see f of two another time,
[00:16:54] maybe lots of times. Let's store that
[00:16:56] result and just return it rather than
[00:16:58] expanding that function tree any further
[00:17:00] and just recursing over and over again
[00:17:03] cuz that would be really really slow.
[00:17:05] Today's episode sponsor is Brilliant.
[00:17:07] And for the longest time, I thought of
[00:17:08] them as a place to learn about math and
[00:17:10] general science. But lately, I've been
[00:17:13] delving into their huge number of
[00:17:14] courses and lessons about coding,
[00:17:16] computers, and AI. This is great stuff,
[00:17:19] and I think the sort of people who watch
[00:17:21] Computer File might like it. You might
[00:17:23] also like it as a gift for other people
[00:17:25] in your life. You can do that, too. You
[00:17:28] know, this stuff is the future for many
[00:17:30] of us. Our careers, our day-to-day
[00:17:33] lives, and Brilliant, with its great
[00:17:35] design and interactive content, they're
[00:17:38] going to put you well on top of it. This
[00:17:40] might be the first step on a new career
[00:17:42] path. To learn for free on Brilliant, go
[00:17:45] to brilliant.org/computile.
[00:17:47] You can also scan the QR code on the
[00:17:49] screen or click on the links below.
[00:17:51] Brilliant's also giving our viewers 20%
[00:17:54] off an annual premium subscription which
[00:17:56] gives you unlimited daily access to
[00:17:58] everything. Our thanks to them for
[00:18:00] supporting computer file.