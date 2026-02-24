import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
    console.log('Fetching recent reviews from database...');
    const reviews = await prisma.review.findMany({
        take: 5,
        orderBy: { createdAt: 'desc' },
        include: { repository: true }
    });

    if (reviews.length === 0) {
        console.log('No reviews found in the database.');
    } else {
        reviews.forEach(review => {
            console.log(`PR #${review.prNumber} [${review.status}] at ${review.createdAt}`);
            if (review.aiResponse) {
                console.log('AI Response:', JSON.stringify(review.aiResponse, null, 2));
            }
        });
    }

    await prisma.$disconnect();
}

main().catch(async (e) => {
    console.error(e);
    await prisma.$disconnect();
    process.exit(1);
});
