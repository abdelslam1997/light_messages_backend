import time
import random

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from faker import Faker

from core_apps.messenger.models import Message
from core_apps.messenger.utils.conversations import get_conversation_id

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = "Seed the database with dummy messages between two users"

    def add_arguments(self, parser):
        parser.add_argument(
            "--sender", type=int, default=1,
            help="Sender user ID (default: 1)"
        )
        parser.add_argument(
            "--receiver", type=int, default=2,
            help="Receiver user ID (default: 2)"
        )
        parser.add_argument(
            "--count", type=int, default=1_000_000,
            help="Number of messages to create (default: 1,000,000)"
        )
        parser.add_argument(
            "--batch-size", type=int, default=10_000,
            help="Batch size for bulk_create (default: 10,000)"
        )
        parser.add_argument(
            "--unread-ratio", type=float, default=0.3,
            help="Ratio of unread messages (default: 0.3)"
        )

    def handle(self, *args, **options):
        sender_id = options["sender"]
        receiver_id = options["receiver"]
        total = options["count"]
        batch_size = options["batch_size"]
        unread_ratio = options["unread_ratio"]

        # Validate users exist
        try:
            sender = User.objects.get(id=sender_id)
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist as e:
            self.stderr.write(self.style.ERROR(f"User not found: {e}"))
            return

        conversation_id = get_conversation_id(sender_id, receiver_id)
        users = [sender, receiver]

        self.stdout.write(
            f"Seeding {total:,} messages between user {sender_id} and user {receiver_id} "
            f"(batch_size={batch_size:,}, unread_ratio={unread_ratio})..."
        )

        created = 0
        start = time.time()

        while created < total:
            current_batch = min(batch_size, total - created)
            messages = []

            for _ in range(current_batch):
                # Randomly pick sender/receiver direction
                s, r = random.sample(users, 2)
                messages.append(Message(
                    sender=s,
                    receiver=r,
                    message=fake.sentence(nb_words=random.randint(3, 25)),
                    read=random.random() > unread_ratio,
                    conversation_id=conversation_id,
                ))

            # bulk_create bypasses .save(), so conversation_id is set above
            Message.objects.bulk_create(messages, ignore_conflicts=False)

            created += current_batch
            elapsed = time.time() - start
            rate = created / elapsed if elapsed > 0 else 0
            self.stdout.write(
                f"  {created:>10,} / {total:,}  "
                f"({created * 100 / total:.1f}%)  "
                f"[{rate:,.0f} msg/s]"
            )

        elapsed = time.time() - start
        self.stdout.write(self.style.SUCCESS(
            f"\nDone! Created {created:,} messages in {elapsed:.1f}s "
            f"({created / elapsed:,.0f} msg/s)"
        ))
